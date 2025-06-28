with open("division_tables.p4", "w") as f:
    for i in range(15, -1, -1):
        f.write(f'''
        action division_step{2**i}(){{
            quotient = (divisor*(quotient + {2**i}) <= dividend) ? quotient + {2**i} : quotient;
        }}

        table division_step_table{2**i} {{
            key = {{}}
            actions = {{
                division_step{2**i};
            }}
            default_action = division_step{2**i};
        }}''')


with open("division_actions.p4", "w") as f:
    for i in range(15, -1, -1):
        f.write(f"\ndivision_step_table{2**i}.apply();")