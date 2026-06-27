import pandas as pd

cp = pd.read_csv('ssd_core/config/competencia_perfil.csv')
cl = pd.read_csv('export/competencia_logro_individual.csv')
cl = cl[cl['ID_EST'] == 'E1']

for periodo in ['2018-1','2018-2','2019-1']:
    print('PERIODO', periodo)
    comp_map = cl[cl['Periodo']==periodo].set_index('ID_COMP')['Logro_Competencia'].to_dict()
    print(comp_map)
    for perfil in ['P1','P2','P3','P4','P5','P6','P7','P8','P9','P10','P11','P12']:
        pcs = cp[cp['perfil_id']==perfil][['ID_COMP','peso']]
        merged = pcs.merge(pd.DataFrame({'ID_COMP': list(comp_map.keys()), 'Logro_Competencia': list(comp_map.values())}), on='ID_COMP', how='inner')
        if merged.empty:
            print(perfil, 'empty')
            continue
        weighted = (merged['Logro_Competencia'] * merged['peso']).sum() / merged['peso'].sum()
        print(perfil, weighted)
