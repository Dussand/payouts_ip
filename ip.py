import streamlit as st
import pandas as pd
import datetime
import re

st.title('CONCILIACIONES PAYOUT')

# Crear pestañas
concDia, concCier, concVal = st.tabs(["📄 Conciliacion al dia", "📄 Conciliacion cierre de dia", "📄 Validaciones Instant Payouts"])

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
    except:
        st.error('Revisa el formato del archivo BCP')



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

        metabase_cierre['num_op'] = metabase_cierre['numero de operacion'].str[-8:]

        #st.dataframe(metabase_cierre, use_container_width=True)

        pivot_mb_cierre = metabase_cierre.pivot_table(
            index = 'fecha_operacion', columns='banco', values='monto', aggfunc = ['sum', 'count']
        ).reset_index()

        st.dataframe(pivot_mb_cierre, use_container_width=True)

        cruce_mb = metabase_cierre[metabase_cierre['banco'] == '(BCP) - Banco de Crédito del Perú'][['fecha_operacion', 'hora_operacion', 'monto', 'num_op', 'inv public_id']]
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
        ).reset_index()

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

        st.header('Subir archivo metabase dias anteriores')
        st.write('''
                 
                 Para poder analizar de manera mas precisa los duplicados se recomienda, en el filtro de fechas,
                 colocar una semana completa, del dia de hoy a 7 dias anteriores. 
                 
                 ''')
        archivo_metabase_semana= st.file_uploader(
        "Subir excel de las operaciones de toda la semana: ", type = ['xlsx', 'xls'],
        key = 'metabase_semana'
    )
        
        if archivo_metabase_semana is not None:
            semana_meta = pd.read_excel(archivo_metabase_semana)
            #filtramos el df por estado pagado y solo yape y bcp
            semana_meta = semana_meta[(semana_meta['estado'] == 'Pagado') & 
                            semana_meta['banco'].isin(['(BCP) - Banco de Crédito del Perú'])]
            semana_meta['num_op'] = semana_meta['numero de operacion'].str.slice(18,27) #agregamos un fila con el numero de operacion extraido de la columna 'numero de operacion'
            
            #utilizaaremos la funcion date para en el siguiente paso filtrar por dia que dejo operaciones 
            hoy = datetime.date.today() 
            hoy_menos_dos = hoy - datetime.timedelta(days=2) #para filtra por el dia a conciliar
            hoy_format = hoy_menos_dos.strftime("%d/%m/%Y") #cambiamos el formato al que tiene el archivo de conciliacion
            hoy_format_str = str(hoy_format) #lo convertimos a string
            #creamos una tabla filtrado por el dia a conciliar
            filtra_sin_duplicados_df = sin_duplicados_df[sin_duplicados_df['fecha_operacion'] == hoy_format_str]

            #filtramos las filas que contienen el mismo numero de operacion en ambas tablas (filtra_sin_duplicados_df y semana_meta)
            coincidencias = filtra_sin_duplicados_df[filtra_sin_duplicados_df['num_op'].isin(semana_meta['num_op'])]
            # Mostrar los resultados en Streamlit
            if len(coincidencias) == len(filtra_sin_duplicados_df): #si ambos tienen las mismas operaciones
                hoy_menos_uno = hoy - datetime.timedelta(days=1)
                hoy_format_uno = hoy_menos_uno.strftime("%d/%m/%Y")
                hoy_format_str_uno = str(hoy_format_uno)
                st.success(f"CONCILIACION {hoy_format_str_uno} COMPLETADA") #conciliacion dia anterior completa 
                st.dataframe(filtra_sin_duplicados_df)
            else:
                st.error('Analizar manualmente')
                inconsistencias = filtra_sin_duplicados_df[~filtra_sin_duplicados_df['num_op'].isin(semana_meta['num_op'])]
                st.dataframe(filtra_sin_duplicados_df, use_container_width=True)

with concVal:
    st.title('📄 Validaciones Instant Payouts')
    st.write('Pagia diseñada para validar pagos de instan payouts en los estados de cuenta')

    # Subir EECC de ALFIN
    st.subheader('Validaciones de pagos de ALFIN')
    eecc_val = st.file_uploader(
        "Subir EECC de ALFIN: ",
        key = 'validaciones'
    )
    # Mostrar el DataFrame del EECC
    if not eecc_val:
        st.warning('Sube el EECC de ALFIN para realizar las validaciones')
    else:
         #leer el excel del eecc
        eecc_val_df = pd.read_excel(eecc_val, skiprows=8)
        #eliminar columnas innecesarias
        eecc_val_df = eecc_val_df[['Fecha', 'Hora', 'Referencia', 'Importe']]  
        #eliminar filas donde la columna 'Referencia' sea NaN
        eecc_val_df = eecc_val_df[eecc_val_df['Referencia'].notna()]
        # Quitar solo el primer cero inicial de la 'Referencia' si lo tiene
        #eecc_val_df['Referencia'] = eecc_val_df['Referencia'].str.replace('^0', '', n=1, regex=True)
        eecc_val_df['Referencia'] = eecc_val_df['Referencia'].str.lstrip('0')
        #extraer el numero de operacion de la columna 'Referencia' quitandole el 0 a la izquierda
        eecc_val_df['num_op'] = eecc_val_df['Referencia'].str.extract(r'(\d{12})')

        #eliminamos el "S/." del importe y convertimos a float
        eecc_val_df['Importe'] = eecc_val_df['Importe'].str.replace('S/', '', regex=False)
        eecc_val_df['monto_str'] = eecc_val_df['Importe'].astype(str).str.replace(r'[.,]', '', regex=True)
        
        #creamos la clave
        eecc_val_df['clave'] = eecc_val_df['num_op'] + eecc_val_df['monto_str'].str[:2]
        
        #+ "-" + eecc_val_df['Hora'].str[-2:]

        # def extraer_hhmm(hora_str):
        #     try:
        #         hora = pd.to_datetime(hora_str)
        #         return hora.strftime('%H%M')
        #     except:
        #         return '0000'
        
        #eecc_val_df['clave'] = eecc_val_df['Hora'].apply(extraer_hhmm) + eecc_val_df['num_op']  # Asegurarse de que num_op tenga 8 dígitos
        st.dataframe(eecc_val_df, use_container_width=True)

        st.subheader('Validar números de operación')        
        num_op_input = st.text_area(
            "Pega aquí los números de operación (una por línea, como vienen desde Excel):",
            placeholder="12345678901234567890\n23456789012345678901\n..."
        )

        if num_op_input:
            #separar por lineas
            filtro_lista = num_op_input.strip().splitlines()
            st.write(f"Se encontraron {len(filtro_lista)} números de operación ingresados.")
            st.write(filtro_lista)
            #limpiar y recortar cada valor a los primeros 8 digitoos
            #filtro_8dig = [val.strip()[:12] for val in filtro_lista if val.strip()]
            #st.write(filtro_8dig)
            # Filtrar el DataFrame por los números de operación ingresados
            validaciones_df = eecc_val_df[eecc_val_df['clave'].isin(filtro_lista)]
            if not validaciones_df.empty:
                st.success(f"Se encontraron {len(validaciones_df)} coincidencias:")
                st.dataframe(validaciones_df[['Fecha', 'Hora', 'Referencia', 'Importe', 'num_op', 'clave']], use_container_width=True)
            else:
                st.warning("No se encontraron coincidencias para los números de operación ingresados.")

        
    # Subir EECC de bcp

    st.subheader('Validaciones de pagos de BCP')

    eecc_val_bcp= st.file_uploader(
        "Subir EECC de BCP: ",
        key = 'validaciones bcp'
    )

    if not eecc_val_bcp:
        st.warning('Sube el EECC de BCP para realizar las validaciones')
    else:
        eecc_val_df_bcp = pd.read_excel(eecc_val_bcp, skiprows=7)
        #convertir la columna 'Operación - Número' a string
        eecc_val_df_bcp['Nº operación'] = eecc_val_df_bcp['Nº operación'].astype(str)
        #clasificar por banco, si empieza con A es BCP, si empieza con YPP es Yape
        def clasificar_banco_bcp(codigo_bcp):
            if codigo_bcp.startswith('A'):
                return 'BCP'
            elif codigo_bcp.startswith('YPP'):
                return 'Yape'
            else:
                return ''
        # Aplicar la función a la columna 'codigo'
        eecc_val_df_bcp['banco'] = eecc_val_df_bcp['Descripción operación'].apply(clasificar_banco_bcp)

        #filtramos solo por bcp
        eecc_val_df_bcp = eecc_val_df_bcp[eecc_val_df_bcp['banco'] == 'BCP']

        #limpiamos la columna descripción operación
        eecc_val_df_bcp['Descripción operación'] = eecc_val_df_bcp['Descripción operación'].str.replace('^A', '', n=1, regex=True)
        #reemplazamos los espacios en blanco por nada para que no afecte al cruce
        eecc_val_df_bcp['Descripción operación'] = eecc_val_df_bcp['Descripción operación'].str.replace(' ', '', regex=True)
        #extraer el numero de operacion de la columna 'Referencia' quitandole el 0 a la izquierda
        eecc_val_df_bcp['num_op'] = eecc_val_df_bcp['Descripción operación'].str.extract(r'(\d{11})')
        eecc_val_df_bcp['Monto'] = eecc_val_df_bcp['Monto'] * -1
        #adaptamos una clave unica junto con el numero de operacion y el monto
        eecc_val_df_bcp['monto_str'] = eecc_val_df_bcp['Monto'].astype(str).str.replace('.', '', regex=False)  # Convertir a string y quitar el punto decimal

        eecc_val_df_bcp['clave'] = eecc_val_df_bcp['num_op'] + eecc_val_df_bcp['monto_str'].str[:2] 

        st.dataframe(eecc_val_df_bcp, use_container_width=True)

        st.subheader('Validar números de operación de BCP')        
        num_op_input_bcp = st.text_area(
            "Pega aquí los números de operación (una por línea, como vienen desde Excel):",
            placeholder="12345678901234567890\n23456789012345678901\n...",
            key='num_op_bcp'
        )

        if num_op_input_bcp:
            #separar por lineas
            filtro_lista_bcp = num_op_input_bcp.strip().splitlines()
            st.write(f"Se encontraron {len(filtro_lista_bcp)} números de operación ingresados.")
            st.write(filtro_lista_bcp)
            #limpiar y recortar cada valor a los primeros 8 digitoos
            #filtro_8dig_bcp = [val.strip()[:8] for val in filtro_lista_bcp if val.strip()]
            #st.write(filtro_8dig_bcp)
            # Filtrar el DataFrame por los números de operación ingresados
            validaciones_df_bcp = eecc_val_df_bcp[eecc_val_df_bcp['clave'].isin(filtro_lista_bcp)]
            if not validaciones_df_bcp.empty:
                st.success(f"Se encontraron {len(validaciones_df_bcp)} coincidencias:")
                st.dataframe(validaciones_df_bcp[['Fecha', 'Descripción operación', 'Monto', 'Nº operación', 'banco', 'clave']], use_container_width=True)
            else:
                st.warning("No se encontraron coincidencias para los números de operación ingresados.")


         
        #st.subheader('Busqueda general de validaciones')
        # st.write('''
        #          Esta tabla contiene las validaciones de pagos de ALFIN y BCP, 
        #          puedes buscar por fecha, hora, referencia, importe, numero de operacion o clave.
        #          ''')
        
        # # Asegurarnos de que las columnas tengan los mismos nombres para poder unir los DataFrames
        
        # # df unido, cambiarmos los nombres de las columnas para que coincidan
        # nuevo_df_bcp =  eecc_val_df_bcp.rename(columns={'Fecha valuta': 'Hora', 'Descripción operación': 'Referencia', 'Monto': 'Importe'})

        # # eliminar columnas innecesarias
        # nuevo_df_bcp = nuevo_df_bcp[['Fecha',
        #                              'Hora', 'Referencia', 'Importe', 'num_op', 'clave']]
        
        # nuevo_df_alfin = eecc_val_df[['Fecha', 'Hora', 'Referencia', 'Importe', 'num_op', 'clave']]

        # # Concatenar los DataFrames verticalmente
        # df_validaciones = pd.concat([nuevo_df_alfin, nuevo_df_bcp], ignore_index=True)
        # st.dataframe(df_validaciones)
        # st.write(len(df_validaciones), 'filas de validaciones de BCP')

        # st.subheader('Validar números de operación de todos los pagos')        
        # num_op_input_general = st.text_area(
        #     "Pega aquí los números de operación (una por línea, como vienen desde Excel):",
        #     placeholder="12345678901234567890\n23456789012345678901\n...",
        #     key='num_op_general'
        # )

 
        # if num_op_input_general:
        #     #separar por lineas
        #     filtro_lista_general = num_op_input_general.strip().splitlines()
        #     st.write(f"Se encontraron {len(filtro_lista_general)} números de operación ingresados.")
        #     st.write(filtro_lista_general)
        #     #limpiar y recortar cada valor a los primeros 8 digitoos
        #     #filtro_8dig_general = [val.strip()[:8] for val in filtro_lista_general if val.strip()]
        #     #st.write(filtro_8dig_general)
        #     # Filtrar el DataFrame por los números de operación ingresados
        #     validaciones_df_general = df_validaciones[df_validaciones['clave'].isin(filtro_lista_general)]
        #     if not validaciones_df_general.empty:
        #         st.success(f"Se encontraron {len(validaciones_df_general)} coincidencias:")
        #         st.dataframe(validaciones_df_general[['Fecha', 'Hora', 'Referencia', 'Importe', 'clave']], use_container_width=True)
        #     else:
        #         st.warning("No se encontraron coincidencias para los números de operación ingresados.")




        







   
         