import streamlit as st
import pandas as pd
import locale

st.title('CONCILIACIONES PAYOUT')

# Crear pestañas
concDia, concCier = st.tabs(["📄 Conciliacion al dia", "📄 Conciliacion cierre de dia"])

with concDia:
    st.subheader('CONCILIACION AL DIA PAYOUTS IP')
    st.divider()
    st.write('Pagina diseñada para revisar que cuadren los montos y cantidades dispersadas con el banco BCP durante las dispersiones de cada hora.')

    st.subheader('METABASE')
    archivo_metabase = st.file_uploader(
        "Subir excel del metabase: ",
        key = 'dia_mb'
    )

    if archivo_metabase is not None:
        #leemos el excel del metabas
        metabase = pd.read_excel(archivo_metabase)
        #filtramos el df por estado pagado y solo yape y bcp
        metabase = metabase[(metabase['estado'] == 'Pagado') & 
                            metabase['banco'].isin(['Yape', '(BCP) - Banco de Crédito del Perú'])]
        
        #creamos una columna solo con la fecha de operacion
        metabase['fecha_operacion'] = metabase['fecha operacion'].dt.date
        # Convertir a datetime
        metabase['fecha_operacion'] = pd.to_datetime(metabase['fecha_operacion'], format='%d-%m-%Y')
        # Extraer el día del mes en español (sin usar locale)
        dias_es = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        metabase['dia_mes'] = pd.to_datetime(metabase['fecha_operacion']).dt.strftime('%A').map(dias_es)

        #creamos una columna solo con la hora de operacion
        metabase['hora_operacion'] = metabase['fecha operacion'].dt.time

        metabase['ultimos_8'] = metabase['numero de operacion'].str[-8:]



        pivot_mb = metabase.pivot_table(
            index = 'fecha_operacion', columns='banco', values='monto', aggfunc = ['sum', 'count']
        )

        st.dataframe(pivot_mb, use_container_width=True)

        cruce_mb = metabase[metabase['banco'] == '(BCP) - Banco de Crédito del Perú'][['fecha_operacion', 'hora_operacion', 'monto', 'ultimos_8']]
        cruce_mb = cruce_mb.rename(columns={'ultimos_8': 'num_op'})
        # Formatear como 'DD/MM/YYYY' y convertir a object
        cruce_mb['fecha_operacion'] = cruce_mb['fecha_operacion'].dt.strftime('%d/%m/%Y')
        cruce_mb['archivo'] = 'metabase'
        #st.dataframe(cruce_mb, use_container_width=True)

        #almacenamos el df exportado en csv para poder descargar y realizar el cruce 
        csv_meta = cruce_mb.to_csv(index=False).encode('utf-8')

        # #creamos el boto
        # descargar_mb = st.download_button(
        #                 label= "Descargar cruce metabase",
        #                 data= csv_meta,
        #                 file_name= f'metabase.csv'
        # )

    st.subheader('BCP')
    archivo_bcp = st.file_uploader(
        "Subir excel de los movimientos de bcp: ", type = ['xlsx', 'xls'],
        key = 'dia_bcp'
    )

    try:
        if archivo_bcp is not None:
            bcp = pd.read_excel(archivo_bcp, skiprows=7)
            # Asegurar que 'Operación - Número' es tipo string
            ##bcp['Operación - Número'] = bcp['Operación - Número'].astype(str)
            # Función para clasificar según el prefijo
            def clasificar_banco(codigo):
                if codigo.startswith('A'):
                    return '(BCP) - Banco de Crédito del Perú'
                elif codigo.startswith('YPP'):
                    return 'Yape'
                else:
                    return ''
                
            # Aplicar la función a la columna 'codigo'
            bcp['banco'] = bcp['Descripción operación'].apply(clasificar_banco)

            # Reemplazar cadenas vacías por NaN
            bcp['banco'].replace('', pd.NA, inplace=True)

            bcp.dropna(subset=['banco'], inplace=True)  
            

            pivot_mb = bcp.pivot_table(
                index = 'Fecha', columns='banco', values='Monto', aggfunc = ['sum', 'count']
            )

            st.dataframe(pivot_mb, use_container_width=True)
            # cruce_bcp = bcp[bcp['banco'] == '(BCP) - Banco de Crédito del Perú'][['Fecha', 'Operación - Hora', 'Monto', 'Operación - Número']]
            # cruce_bcp = cruce_bcp.rename(columns={'Fecha':'fecha_operacion','Operación - Hora':'hora_operacion', 'Monto':'monto' ,'Operación - Número': 'num_op'})
            # cruce_bcp['num_op'] = cruce_bcp['num_op'].astype(str).str.zfill(8)
            # cruce_bcp['archivo'] = 'bcp'
            # #st.dataframe(cruce_bcp, use_container_width=True)

            # #almacenamos el df exportado en csv para poder descargar y realizar el cruce 
            # csv_bcp = cruce_bcp.to_csv(index=False).encode('utf-8')

            # #creamos el boto
            # descargar_bcp = st.download_button(
            #                 label= "Descargar cruce BCP",
            #                 data= csv_bcp,
            #                 file_name= f'bcp.csv'
            # )

            # # Concatenar los DataFrames verticalmente
            # df = pd.concat([cruce_mb, cruce_bcp], ignore_index=True)

            # # Identificar duplicados en la columna 'num_op'
            # df['duplicado'] = df['num_op'].duplicated(keep=False)
            
            # # Filtrar filas sin duplicados en 'num_op'
            # sin_duplicados_df = df[~df['num_op'].duplicated(keep=False)]

            # st.write("### Filas sin valores duplicados")
            # st.dataframe(sin_duplicados_df)


            # #almacenamos el df exportado en csv para poder descargar y realizar el cruce 
            # csv_concat = sin_duplicados_df.to_csv(index=False).encode('utf-8')

            # #creamos el boto
            # descargar_bcp = st.download_button(
            #                 label= "Descargar conciliacion del cierre",
            #                 data= csv_concat,
            #                 file_name= f'Conciliacion_cierre.csv'
            # )
    except:
        st.write('Revisa el formato del archivo BCP')



with concCier:
    st.subheader('CONCILIACION CIERRE DE DIA PAYOUTS IP')
    st.divider()
    st.write('Pagina diseñada para revisar que cuadren los montos y cantidades dispersadas con el banco BCP.')

    st.subheader('METABASE')
    archivo_metabase_cierre = st.file_uploader(
        "Subir excel del metabase: ",
        key = 'cierre'
    )

    if archivo_metabase_cierre is not None:
        #leemos el excel del metabas
        metabase_cierre = pd.read_excel(archivo_metabase_cierre)
        #filtramos el df por estado pagado y solo yape y bcp
        metabase_cierre = metabase_cierre[(metabase_cierre['estado'] == 'Pagado') & 
                            metabase_cierre['banco'].isin(['Yape', '(BCP) - Banco de Crédito del Perú'])]
        
         #creamos una columna solo con la fecha de operacion
        metabase_cierre['fecha_operacion'] = metabase_cierre['fecha operacion'].dt.date
        # Convertir a datetime
        metabase_cierre['fecha_operacion'] = pd.to_datetime(metabase_cierre['fecha_operacion'], format='%d-%m-%Y')
        # Extraer el día del mes en español (sin usar locale)
        dias_es = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        metabase_cierre['dia_mes'] = pd.to_datetime(metabase_cierre['fecha_operacion']).dt.strftime('%A').map(dias_es)

        metabase_cierre['hora_operacion'] = metabase_cierre['fecha operacion'].dt.time

        metabase_cierre['ultimos_8'] = metabase_cierre['numero de operacion'].str[-8:]



        pivot_mb_cierre = metabase_cierre.pivot_table(
            index = 'fecha_operacion', columns='banco', values='monto', aggfunc = ['sum', 'count']
        )

        st.dataframe(pivot_mb_cierre, use_container_width=True)

        cruce_mb = metabase_cierre[metabase_cierre['banco'] == '(BCP) - Banco de Crédito del Perú'][['fecha_operacion', 'hora_operacion', 'monto', 'ultimos_8']]
        cruce_mb = cruce_mb.rename(columns={'ultimos_8': 'num_op'})
        # Formatear como 'DD/MM/YYYY' y convertir a object
        cruce_mb['fecha_operacion'] = cruce_mb['fecha_operacion'].dt.strftime('%d/%m/%Y')
        cruce_mb['archivo'] = 'metabase'
        #st.dataframe(cruce_mb, use_container_width=True)

        #almacenamos el df exportado en csv para poder descargar y realizar el cruce 
        csv_meta = cruce_mb.to_csv(index=False).encode('utf-8')

        #creamos el boto
        descargar_mb = st.download_button(
                        label= "Descargar cruce metabase",
                        data= csv_meta,
                        file_name= f'metabase.csv'
        )
    else: 
        st.warning('Sube tu archivo')

    st.subheader('BCP')
    archivo_bcp_cierre = st.file_uploader(
        "Subir excel de los movimientos de bcp: ", type = ['xlsx', 'xls'],
        key = 'cierre_bcp'
    )

    if archivo_bcp_cierre is not None:
        bcp_cierre = pd.read_excel(archivo_bcp_cierre, skiprows=4)
        # Asegurar que 'Operación - Número' es tipo string
        ##bcp['Operación - Número'] = bcp['Operación - Número'].astype(str)
        # Función para clasificar según el prefijo
        
        def clasificar_banco(codigo_cierre):
            if codigo_cierre.startswith('A'):
                return '(BCP) - Banco de Crédito del Perú'
            elif codigo_cierre.startswith('YPP'):
                return 'Yape'
            else:
                return ''
            
        # Aplicar la función a la columna 'codigo'
        bcp_cierre['banco'] = bcp_cierre['Descripción operación'].apply(clasificar_banco)

        # Reemplazar cadenas vacías por NaN
        bcp_cierre['banco'].replace('', pd.NA, inplace=True)

        bcp_cierre.dropna(subset=['banco'], inplace=True)  
        
      
        pivot_mb = bcp_cierre.pivot_table(
            index = 'Fecha', columns='banco', values='Monto', aggfunc = ['sum', 'count']
        )

        st.dataframe(pivot_mb, use_container_width=True)
        cruce_bcp = bcp_cierre[bcp_cierre['banco'] == '(BCP) - Banco de Crédito del Perú'][['Fecha', 'Operación - Hora', 'Monto', 'Operación - Número']]
        cruce_bcp = cruce_bcp.rename(columns={'Fecha':'fecha_operacion','Operación - Hora':'hora_operacion', 'Monto':'monto' ,'Operación - Número': 'num_op'})
        cruce_bcp['num_op'] = cruce_bcp['num_op'].astype(str).str.zfill(8)
        cruce_bcp['archivo'] = 'bcp'
        #st.dataframe(cruce_bcp, use_container_width=True)

        #almacenamos el df exportado en csv para poder descargar y realizar el cruce 
        csv_bcp = cruce_bcp.to_csv(index=False).encode('utf-8')

        #creamos el boto
        descargar_bcp = st.download_button(
                        label= "Descargar cruce BCP",
                        data= csv_bcp,
                        file_name= f'bcp.csv'
        )

        # Concatenar los DataFrames verticalmente
        df = pd.concat([cruce_mb, cruce_bcp], ignore_index=True)

        # Identificar duplicados en la columna 'num_op'
        df['duplicado'] = df['num_op'].duplicated(keep=False)
        
        # Filtrar filas sin duplicados en 'num_op'
        sin_duplicados_df = df[~df['num_op'].duplicated(keep=False)]

        st.write("### Filas sin valores duplicados")
        st.write('Movimientos que se realizaron despues de la hora de corte de cada dia (9:18 pm). ')
        
        st.dataframe(sin_duplicados_df, use_container_width=True)
        st.warning('Descargar y guardar para cuadrar mañana con la conciliacion del cierre de hoy.')

        #almacenamos el df exportado en csv para poder descargar y realizar el cruce 
        csv_concat = sin_duplicados_df.to_csv(index=False).encode('utf-8')

        #creamos el boto
        descargar_bcp = st.download_button(
                        label= "Descargar conciliacion del cierre",
                        data= csv_concat,
                        file_name= f'Conciliacion_cierre.csv'
        )

    else: 
        st.warning('Sube tu archivo')



