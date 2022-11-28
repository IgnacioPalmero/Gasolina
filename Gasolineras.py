import requests
import datetime
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#Fecha
t = datetime.datetime.now()
fecha = t.strftime('%d/%m/%Y')

#Recoger los datos
x = requests.get('https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroMunicipio/5324')
js = json.loads(x.text)

df= pd.DataFrame(js['ListaEESSPrecio'])


#Reemplaza los espacios vacios por NaN
df.replace("",np.nan, inplace=True)

lista_gasolinas = ["Precio Gasoleo A", "Precio Gasoleo Premium", "Precio Gasolina 95 E5", "Precio Gasolina 98 E5"]


lista_data_def = list()

for i in lista_gasolinas:
    #Elegir la columna y preparar los datos para poder operar con ellos
    df[i] = df[i].str.replace(",",".")
    df[i] = df[i].astype("float")
    


    #Tabla definitiva
    df_def = df[["Dirección", i]].set_index("Dirección").T


    #Calcular media, max y min y añadir las columnas
    df_def["Precio medio"] = round(df[i].mean(),3)
    df_def["Precio máximo"] = df[i].max()
    df_def["Precio mínimo"] = df[i].min()
    df_def.insert(0, 'Fecha', fecha)
    
    lista_data_def.append(df_def)
    

#Si existe ya el archivo añade una nueva fila
try:
    
    df_historico_lista = list()
    
    for enum, i in enumerate(lista_gasolinas):
        df_anterior = pd.read_excel("Precios gasolinas.xlsx", sheet_name = i)

        df_historico_lista.append(pd.concat([df_anterior, lista_data_def[enum]], axis = 0))
        
        #Seguro por si le das dos veces el mismo día
        df_historico_lista[enum].reset_index(inplace=True)
        df_historico_lista[enum].drop("index",axis=1,inplace=True)
        df_historico_lista[enum].drop_duplicates(inplace=True)


    writer = pd.ExcelWriter('Precios gasolinas.xlsx', engine='xlsxwriter')

    for i in range(len(lista_gasolinas)):
        df_historico_lista[i].to_excel(writer, sheet_name = lista_gasolinas[i], index=False)

    writer.save()
        

#Si no existe crea el archivo nuevo con la fila de hoy
except:
    
    writer = pd.ExcelWriter('Precios gasolinas.xlsx', engine='xlsxwriter')
    
    for i in range(len(lista_gasolinas)):
        lista_data_def[i].to_excel(writer, sheet_name = lista_gasolinas[i], index=False)

    writer.save()
    

#Gráfica de cajas
for i in lista_gasolinas:
    df[i] = df[i].fillna(df[i].mean())

df2 = df[["Precio Gasoleo A", "Precio Gasoleo Premium", "Precio Gasolina 95 E5", "Precio Gasolina 98 E5"]]


plt.figure(figsize=(15,10))
data = df2.iloc[:, :]
etiquetas = df2.columns[:]

plt.boxplot(x = data, labels = etiquetas, meanline=True)
plt.show()