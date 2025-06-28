
        action division_step32768(){
            quotient = (divisor*(quotient + 32768) <= dividend) ? quotient + 32768 : quotient;
        }

        table division_step_table32768 {
            key = {}
            actions = {
                division_step32768;
            }
            default_action = division_step32768;
        }
        action division_step16384(){
            quotient = (divisor*(quotient + 16384) <= dividend) ? quotient + 16384 : quotient;
        }

        table division_step_table16384 {
            key = {}
            actions = {
                division_step16384;
            }
            default_action = division_step16384;
        }
        action division_step8192(){
            quotient = (divisor*(quotient + 8192) <= dividend) ? quotient + 8192 : quotient;
        }

        table division_step_table8192 {
            key = {}
            actions = {
                division_step8192;
            }
            default_action = division_step8192;
        }
        action division_step4096(){
            quotient = (divisor*(quotient + 4096) <= dividend) ? quotient + 4096 : quotient;
        }

        table division_step_table4096 {
            key = {}
            actions = {
                division_step4096;
            }
            default_action = division_step4096;
        }
        action division_step2048(){
            quotient = (divisor*(quotient + 2048) <= dividend) ? quotient + 2048 : quotient;
        }

        table division_step_table2048 {
            key = {}
            actions = {
                division_step2048;
            }
            default_action = division_step2048;
        }
        action division_step1024(){
            quotient = (divisor*(quotient + 1024) <= dividend) ? quotient + 1024 : quotient;
        }

        table division_step_table1024 {
            key = {}
            actions = {
                division_step1024;
            }
            default_action = division_step1024;
        }
        action division_step512(){
            quotient = (divisor*(quotient + 512) <= dividend) ? quotient + 512 : quotient;
        }

        table division_step_table512 {
            key = {}
            actions = {
                division_step512;
            }
            default_action = division_step512;
        }
        action division_step256(){
            quotient = (divisor*(quotient + 256) <= dividend) ? quotient + 256 : quotient;
        }

        table division_step_table256 {
            key = {}
            actions = {
                division_step256;
            }
            default_action = division_step256;
        }
        action division_step128(){
            quotient = (divisor*(quotient + 128) <= dividend) ? quotient + 128 : quotient;
        }

        table division_step_table128 {
            key = {}
            actions = {
                division_step128;
            }
            default_action = division_step128;
        }
        action division_step64(){
            quotient = (divisor*(quotient + 64) <= dividend) ? quotient + 64 : quotient;
        }

        table division_step_table64 {
            key = {}
            actions = {
                division_step64;
            }
            default_action = division_step64;
        }
        action division_step32(){
            quotient = (divisor*(quotient + 32) <= dividend) ? quotient + 32 : quotient;
        }

        table division_step_table32 {
            key = {}
            actions = {
                division_step32;
            }
            default_action = division_step32;
        }
        action division_step16(){
            quotient = (divisor*(quotient + 16) <= dividend) ? quotient + 16 : quotient;
        }

        table division_step_table16 {
            key = {}
            actions = {
                division_step16;
            }
            default_action = division_step16;
        }
        action division_step8(){
            quotient = (divisor*(quotient + 8) <= dividend) ? quotient + 8 : quotient;
        }

        table division_step_table8 {
            key = {}
            actions = {
                division_step8;
            }
            default_action = division_step8;
        }
        action division_step4(){
            quotient = (divisor*(quotient + 4) <= dividend) ? quotient + 4 : quotient;
        }

        table division_step_table4 {
            key = {}
            actions = {
                division_step4;
            }
            default_action = division_step4;
        }
        action division_step2(){
            quotient = (divisor*(quotient + 2) <= dividend) ? quotient + 2 : quotient;
        }

        table division_step_table2 {
            key = {}
            actions = {
                division_step2;
            }
            default_action = division_step2;
        }
        action division_step1(){
            quotient = (divisor*(quotient + 1) <= dividend) ? quotient + 1 : quotient;
        }

        table division_step_table1 {
            key = {}
            actions = {
                division_step1;
            }
            default_action = division_step1;
        }