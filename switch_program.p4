// SPDX-License-Identifier: Apache-2.0

//Original source: https://github.com/p4lang/tutorials
/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<8> TYPE_PPV = 0x094;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ppv_t {
    bit<32> value;
    bit<8> protocol;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<6>    diffserv;
    bit<2>    ecn;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

struct metadata {
    bit<64> meter_tag;
}

struct headers {
    ethernet_t   ethernet;
    ppv_t        ppv;
    ipv4_t       ipv4;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
              out headers hdr,
              inout metadata meta,
              inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            TYPE_PPV: parse_ppv;
            default: accept;
        }
    }

    state parse_ppv {
        packet.extract(hdr.ppv);
        transition accept;
    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    direct_meter<bit<64>>(MeterType.bytes) my_meter;

    register<bit<32>>(1) minimum_ppv_reg;
    register<bit<32>>(65) future_bins;
    register<bit<32>>(65) old_bins;
    bit<32> minimum_ppv;
    bit<32> new_minimum_ppv_value;
    bit<32> middle_point;

    bit<64> dividend;
    bit<64> divisor;
    bit<64> quotient;
    bit<64> step;

    bit<32> old_bin0;
    bit<32> old_bin1;
    bit<32> old_bin2;
    bit<32> old_bin3;
    bit<32> old_bin4;
    bit<32> future_bin;

    bit<3> current_bin;

    bit<32> low;
    bit<32> high;

    bit<32> random_value;
    bit<32> randomized_throughput;
    bit<32> mod_result;

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action ppv_mark(bit<32> value){
        hdr.ppv.setValid();

        hdr.ppv.protocol = hdr.ipv4.protocol;
        hdr.ppv.value = value;
        hdr.ipv4.protocol = TYPE_PPV;
    }

    action ppv_demark(){
        hdr.ipv4.protocol = hdr.ppv.protocol;
        hdr.ppv.setInvalid();
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    action m_action() {
        my_meter.read(meta.meter_tag);
    }

    table ipv4_meter {
        key = {
            hdr.ipv4.srcAddr: lpm;
        }
        actions = {
            m_action;
            NoAction;
        }
        default_action = NoAction;
        meters = my_meter;
        size = 16384;
    }

    action overloaded() {
        drop();
    }

    action packet_accept() {
    }

    table meter_filter {
        key = {
            meta.meter_tag: exact;
        }
        actions = {
            overloaded;
            packet_accept;
        }
        default_action = packet_accept;
        size = 16;
    }

    table ppv_marker {
        key = {
            hdr.ipv4.srcAddr: lpm;
            hdr.ipv4.protocol: exact;
        }
        actions = {
            ppv_mark;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction;
    }

    #include "division_tables.p4"

    action ppv_remark1(bit<4> traffic_type, bit<8> bin_number) {


        //0: golden
        //1: silver
        old_bins.read(old_bin0, (bit<32>) bin_number*5);
        old_bins.read(old_bin1, (bit<32>) bin_number*5+1);
        old_bins.read(old_bin2, (bit<32>) bin_number*5+2);
        old_bins.read(old_bin3, (bit<32>) bin_number*5+3);
        old_bins.read(old_bin4, (bit<32>) bin_number*5+4);
        low = 0;
        if(hdr.ppv.value <= 13107){
            low = old_bin1+old_bin2+old_bin3+old_bin4;
            high = low + old_bin0;
            current_bin = 0;
        } else if(hdr.ppv.value <= 26214){
            low = old_bin2+old_bin3+old_bin4;
            high = low + old_bin1;
            current_bin = 1;
        } else if(hdr.ppv.value <= 39321){
            low = old_bin3+old_bin4;
            high = low + old_bin2;
            current_bin = 2;
        } else if(hdr.ppv.value <= 52428){
            low = old_bin4;
            high = low + old_bin3;
            current_bin = 3;
        } else {
            low = 0;
            high = old_bin4;
            current_bin = 4;
        }
        
        random(randomized_throughput, low, high);

        divisor = (bit<64>)randomized_throughput+900;
        quotient = 0;

        if(traffic_type == 0){
           dividend = 65535*900;
        } else {
           dividend = 65535*900/2;
        }
    }

    action ppv_remark2(bit<4> traffic_type, bit<8> bin_number) {
        hdr.ppv.value = (bit<32>)quotient;

        future_bins.read(future_bin, (bit<32>) bin_number*5+(bit<32>)current_bin);

        future_bins.write((bit<32>) bin_number*5+(bit<32>)current_bin, future_bin+(bit<32>)hdr.ipv4.totalLen);
    }

    table ppv_remarker1 {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            ppv_remark1;
            NoAction;
        }
        size = 1024;
        default_action = NoAction;
    }

    table ppv_remarker2 {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            ppv_remark2;
            NoAction;
        }
        size = 1024;
        default_action = NoAction;
    }

    table ppv_demarker {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ppv_demark;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction;
    }

    action ppv_based_drop(){
        if(hdr.ppv.value < minimum_ppv){
            standard_metadata.egress_spec = 0;
        }
    }

    apply {
        if (hdr.ipv4.isValid()) {
            ipv4_lpm.apply();
            ppv_marker.apply();
            minimum_ppv_reg.read(minimum_ppv, (bit<32>) 0);
            new_minimum_ppv_value = minimum_ppv;
            if (hdr.ppv.isValid()) {
                ppv_remarker1.apply();

                #include "division_actions.p4"

                ppv_remarker2.apply();
                ppv_based_drop();
                if(standard_metadata.egress_spec != 0){
                    ipv4_meter.apply();
                    if(meta.meter_tag >= 1){
                        hdr.ipv4.ecn = 3;
                        if(new_minimum_ppv_value+1 < hdr.ppv.value) {
                            new_minimum_ppv_value = new_minimum_ppv_value + 1;
                        }
                        if(meta.meter_tag == 2){
                            if(new_minimum_ppv_value+10 < hdr.ppv.value) {
                                new_minimum_ppv_value = new_minimum_ppv_value + 10;
                            }
                        }
                    } else 
                    meter_filter.apply();
                    ppv_demarker.apply();
                }
            } 
            minimum_ppv_reg.write((bit<32>) 0, new_minimum_ppv_value);
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    apply {
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
        update_checksum(
        hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.ecn,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.ppv);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
