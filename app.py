#libreria para la creacion de la pagina
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def main():
    #Configura valores basicos de la pagina
    st.set_page_config(
        page_title="Método Simplex",
        page_icon="🤖"
    )
    # Página incial

    ##titulo de la pagina
    st.title('Método simplex')
    
    # Selección del método
    metodo = st.selectbox('Método',('Penalización (Gran M)','Dos fases'))
    
    if metodo == 'Penalización (Gran M)':
        M = st.number_input('Inserte el valor de M',min_value=1,value=999999999999)
    
    ## Entrada de número de variables y restricciones
    ### recuadros de recogida de texto que guarda en variables
    #x = variables, r=restricciones
    x = st.number_input('Inserte número de variables',min_value=1)#valor minimo para evitar problemas
    r = st.number_input('Inserte número de restricciones', min_value=1)
    
    # Selección de objetivo (Maximizar o Minimizar)    
    obj = st.selectbox('¿Cuál es el objetivo de la función?', ('Maximizar','Minimizar'))
    
    ### control para saber las dimensiones, esto para poder saber si es posible graficar
    if x == 2:
        margen = st.number_input('Amplitud de la gráfica', min_value=1, value=10)
    else:
    ### margen para determinar el limite de graficacion 
        margen = 0
    # Entrada de la función objetivo    
    st.write('### Función Objetivo')#escritura con marlon en la pagina
    #funcion objetivo
    FO = np.empty((1, x)) #matriz vacia para la funcion objetivo y guardar los cocientes
    #elemento que crea columnas segun las variables que requiramos para la FO
    col_FO = st.columns(x, gap='small')
    for j in range(0, x):
        #creacion de las columnas a partir del numero de variables
        FO[0,j] = col_FO[j].number_input(f'$x_{{{j+1}}}$', key=f'col_FO{j}')
                                        #$para codigo latex
    
    # Entrada de restricciones    
    col = [] #elemento para las columnas, guarda la linea de las resticciones
    option = [] #eleccion de la desigualdad
    rest = []   #Lado derecho (valor de la restriccion)
    arr = np.empty((r, x)) #matriz A, r=numero de restricciones
    k=0 #variable de control Infly
    for i in range(0,r):
        st.write(f'#### Restricción {i+1}')#escribe "restriccion"
        col.append(st.columns(x + 2, gap='small')) #Columnas
        for j in range(0, x):
            arr[i,j] = col[i][j].number_input(f'$x_{{{j+1}}}$', key=k)#en las columnas formadas va asignando los valores           
            k+=1
        option.append(col[i][x].selectbox('',('<=', '=', '>='), key=k))#evalua y coloca la desigualdad
        rest.append(col[i][x+1].number_input('', key=k+1))#agrega el "lado derecho" de la restriccion
        k+=2
        
    # Botón para continuar con el método simplex        
    if st.button("Continuar",key='boton1'):
        #funcion para la revision del metodo que se usara
        if metodo == 'Penalización (Gran M)':
            metodo_simplex_penalizacion(M,x,r,obj,FO,arr,option,rest,margen)
        
#inicializacion del metodo simplex de penalizacion
def metodo_simplex_penalizacion(M,x,r,obj,FO,arr,option,rest,margen):
    #variables de control sin estandarizar
    x_a = x #guardamos las variables del problema sin estadarizar
    restricciones = arr.copy() #guardamos las restricciones sin estandarizar
    FO_original = FO.copy() #guardamos la funcion objetivo original sin estandarizar
    # Inicialización de variable M en función del objetivo   
    # M=penzalizacion, en funcion del objetivo se cambia el valor de M 
    if obj == 'Maximizar':
        M = -M
    elif obj == 'Minimizar':
        M = M
    
    #Estandarizar
    x,r,FO,arr,option,rest = estandarizar(x,r,FO,arr,option,rest,M)
    #finalizamos las variables ya estandarizadas
    
    # Mostrar estandarizado  
    st.write('### Estandarizado')
    st.write('##### Función objetivo')
    
    # ... Código para mostrar la función objetivo y restricciones estandarizadas
    texto_FO = f'${obj}$ $Z =' #imprime el objetivo de la FO (max o min)
    for i in range(x-1): #la ultima iteracion se realiza por fuera
        #evaluamos el valor del siguiente cociente
        if FO[0,i+1] >= 0:
            #si el valor es positivo solo ponemos el numero,la variable, y el signo de +
            texto_FO += f'{FO[0,i]}x_{{{i+1}}}+'
        else:
            #si el valor es negativo, ponemos el numero, variable y continua con la iteracion (la siguiente viene con el valor negativo)
            texto_FO += f'{FO[0,i]}x_{{{i+1}}}'
    #añadimos el ultimo cociente con la variable
    texto_FO += f'{FO[0,x-1]}x_{{{x}}}$'
    st.write(texto_FO) #imprimir
    
    #la impresion de estos valores es  la misma logica anterior
    st.write('##### Restricciones')
    for i in range(r):
        texto_r = f'{i+1}. $'
        for j in range(x-1):
            if arr[i,j+1] >= 0:
                texto_r += f'{arr[i,j]}x_{{{j+1}}}+'
            else:
                texto_r += f'{arr[i,j]}x_{{{j+1}}}'
        texto_r += f'{arr[i,x-1]}x_{{{x}}}={rest[i]}$'#la diferencia es el que añadimos el valor derecho de la desigualdad
        st.write(texto_r)
        
    # Preparar tablero inicial
    var_bas,Cj,b,A,k,tablero = preparar_tablero(x,x_a,r,obj,FO,arr,option,rest,M)
    if k == 0:
        st.write('No hay variables basicas')
        return 
    b_r = b.copy() #guarda los datos del "lado derecho"

    # Bucle para aplicar el método simplex
    h = 0 #variable de control de iteraciones
    opt_encontrado = False #control de hayar solucion
    while True:
    #for p in range(5):
        if h > 10000: #criterio de parada de iteraciones
            st.write('### :red[Error!: No se pudo encontrar una solución óptima]')
            break
        Zj = np.round(calcular_Zj(var_bas,arr,x,b_r,Cj),14) #calcula Zj
        # round = redondea a 14 cifras decimales criticas
        #st.write('Zj',Zj)
        Zj_Cj = np.round(calcular_Zj_Cj(Zj,Cj,x),14) #calcula Zj-cj
        #st.write('Zj_Cj',Zj_Cj)
        
        base = seleccionar_base(obj,Zj_Cj,x) #busca la posicion de la nueva base
        #st.write('base',base)
        co_min = np.round(cociente_minimo(b_r,arr,base,r),10) 
        #conseguimos el vector con los cocientes minimos y la posicion del elegido
        
        #st.write('co_min',co_min)
        tablero += graficar_tablero(var_bas,Cj,x,r,arr,b_r, Zj,Zj_Cj, base,co_min)#graficar tablero     
        
        if co_min[0,r] == -1:
        #cuando nos devuelve un cociente minimo que no cumpla las caracteristicas
            st.write('### :red[Error!: Problema no acotado]')
            st.write(tablero)
            break
        
        if prueba_optimalidad(obj,Zj_Cj,x):
            st.write(tablero)
            opt_encontrado = True #cambiamos variable de control del bucle
            break #rompemos el bucle
           
        ## Cambio de base
        #st.write(var_bas)
        k=0 #variable de control
        for i in range(x):
            #var_bas = vector de las variables basicas
            if var_bas[0,i] == 1:
            #comprobamos si es una variable basica
                if k == co_min[0,r]:
                    #si el cociente minimo es = a k
                    var_bas[0,i] = 0 #la convierte en 0 sacandola de la base
                    var_bas[0,base] = 1 #y convierte en uno la que entra
                    break
                else:
                    k += 1
        #st.write('var_bas',var_bas)                
        
        B_inv = obtener_B_inv(A,var_bas,r,x)
        #st.write('B_inv',B_inv)
        #st.write('A',A)
        #st.write('b',b)
        arr = np.round(np.dot(B_inv,A),14) #multiplicamos A*Binversa
        b_r = np.round(np.dot(B_inv,b),14) #multiplicamos b*Binversa
        
        
        #st.write(arr)
        h += 1 #contador de criterio de parada
    
    #fuera del bucle
    #st.write(tablero)
    solucion_Z = 0 #solucion del problema
    if opt_encontrado:
        #evaluamos si tenemos solucion optima
        CB = obtener_CB(var_bas,x,Cj) #obtenemos el CB
        Factible = True
        for i in CB:
            #st.write(i,M)
            if i == M:
            #si encontramos una variable artifical en las basicas es no factible
                #st.write(obtener_CB(var_bas,x,Cj))
                st.write('### :red[Error! No hay solución factible]')                
                factible = False
                #para poder graficar
                solucion = np.full((1,x_a),margen-(0.2*margen))            
                Factible = False
                break
        if Factible:
            #si la solucion es factible
            st.write('### Solución optima')
            factible = True
            st.write(f'$Z = {Zj[0,x]}$')
            solucion_Z = Zj[0,x] #el ultimo valor de Zj
            m = 0
            solucion = np.zeros((1,x_a))
            for i in range(x_a):
                if var_bas[0,i] == 1:
                    #si en las basicas hay una variable del problema imprime su valor
                    st.write(f'$x_{{{i+1}}}={b_r[m]}$')
                    solucion[0,i] = b_r[m]
                    m+=1
                else:
                    #si no su valor es 0
                    st.write(f'$x_{{{i+1}}}=0$')
                    solucion[0,i] = 0
    else:
        #no se encontro una solucion optima
        factible = False
        solucion = np.full((1,x_a),margen-(0.2*margen))            
    crear_grafica(x_a,r,solucion,restricciones,b,option,factible,margen,FO_original,solucion_Z)
        
    
def estandarizar(x,r,FO,arr,option,rest, M):

    # Cambio de signo cuando el lado derecho es negativo
    for i in range(r):
        if rest[i] < 0:
            #multiplicamos el lado izquierdo a negativo
            rest[i] = rest[i]*-1
            arr[i] = arr[i]*-1
            #giramos la desigualdad 
            if option[i] == '<=':
                option[i] = '>='
            elif option[i] == '>=':
                option[i] = '<='    
    
    # Cantidad de variables que agregaremos
    var_agr = x 
    #variable de control, para determinar cuantas variables habra al estandarizar
    art = 0 #numero de variables artificiales
    for o in option:
        #evaluacion de desigualdades para agregar variables
        if o == '<=':
            var_agr += 1    #1 de holgura
        elif o == '=':
            var_agr += 1    #1 artificial
            art += 1
        elif o == '>=':
            var_agr += 2    #1 de exceso y 1 artificial                
            art += 1
            
    #Estandarizamos las restricciones
    a = np.zeros((r,var_agr)) 
    #creacion de la matriz (vacia) de las variables + las variables agregadas x las restricciones
    a[:,:x] = arr #añadimos a la matriz los valores de arr
    var_art = np.zeros((1,art)) 
    #variable de control, vector donde guardamos las posiciones de las variables artificiales
    #st.write(var_art) #debug
    #variables de control
    var_art_i = 0 #contador de variables artificiales
    columna = 0 
    #iteramos en restricciones
    for i in range(r):
        #abarcamos el rango de las variables agregadas y no toda la matriz
        for j in range(x+i):
            #evalua la desigualdad
            if option[i] == '<=': #añade una de holgura
                a[i,x+columna]=1
                break
            elif option[i] == '=': #añade una artifical
                a[i,x+columna]=1
                #guardamos la posicion en la que se coloca
                var_art[0,var_art_i] = x+columna
                #suma de contador
                var_art_i += 1
                break
            elif option[i] == '>=': #añadimos exceso y artificial
                #la variable de exceso es negativa
                a[i,x+columna]=-1
                #le sumamos una artificial
                a[i,x+columna+1]=1
                #guardamos la poscision de la artifical que es la columna +1
                var_art[0,var_art_i] = x+columna+1
                #suma de contador
                var_art_i += 1
                #desplazamos el apuntador de columna ya que se añadieron dos variables
                columna += 1
                break
        #aumenta el apuntador en 1
        columna += 1
    #st.write(a) #debug
    arr = a #guardamos la matriz estandarizada en la matriz A anteriormente creada
    
    #Estandarizamos la FO
    b = np.zeros((1,var_agr)) #variable de control, vector = a las variables de FO + variables agregadas
    b[:,:x] = FO #guardamos los cocientes de la FO
    
    FO = b #sobreescribimos la FO
    x = var_agr #sobreescribimos las variables con las variables agregadas
    #st.write(var_art) #debug
    for i in range(art):
        #buscamos la posicion de las variables artificiales para añadir la penalizacion
        FO[0,int(var_art[0,i])] = M

    #st.write(FO) #debug
    #retorna todo estandarizado
    return x,r,FO,arr,option,rest  
    
def preparar_tablero(x,x_a,r,obj,FO,arr,option,rest,M):
    #definimos las 3 matrices para la solucion
    Cj = FO #cocientes de la FO
    b = rest #"lado derecho de las restricciones"
    A = arr #matriz A
    
    #Determinar las basicas
    var_bas = np.zeros((1,x)) #vector del tamaño x
    for i in range(x):
        k = 0 #variable de control
        for j in range(r):  
            #x_a control de variables originales
            if i <= x_a-1: #control para ignorar las variables originales
                break          
            if arr[j,i] != 0 and arr[j,i] != 1:
            #si el cociente es diferente de 0 y 1, el valor es -1
                k = 99 #descarta la variable para no ser basica, por no ser 0 ni 1
                break
            elif arr[j,i] == 1:
            #con un valor de uno se hace contador como posible basica
                k += 1
        if k == 1:
        #cumpliendo con las restricciones de basicas, si el contador es 1 es una basica, y se guarda su posicion con el vector paralelo
           var_bas[0,i] = 1
    
    k=0
    for v in var_bas:
    #contador de las variables basicas que hay
        if (v == 1).any():
            k+=1
            
    tablero = '' #String de todo el proceso que se imprime
    if k == 0: #sin variables basicas termina el proceso
        return var_bas, Cj, b, A, 0,tablero
    else:
        ## Graficación de tablero
        st.write('### Tablero')
        #con el lenguaje Markdown y streamlit graficamos la tabla simplex
        tablero = f'| | $C_j$ |' #$ indica lenguaje latex
        for i in range(x):
            tablero += f' {Cj[0,i]} |'
        tablero += '| |'
        tablero += '\n|---|---|'
        for i in range(x):
            tablero += f'---|'
        tablero += '---|---|'
        
        tablero += '\n|$C_B$|$x_B$|'
        for i in range(x):
            tablero += f' $x_{i+1}$ |'
        tablero += '$b$|Cociente minimo|'
        #retorno de las variables modificadas, el tablero, y el numero '1' indica el encuentro de var. basicas
        return var_bas, Cj,b,A,1,tablero

def obtener_CB(var_bas,x,Cj):
    CB = [] #matriz
    for i in range(x):
        #busca la posicion de las basicas
        if var_bas[0,i] == 1:
            CB.append(Cj[0,i])  #agrega el valor de las basicas en CB          
    #st.write(CB)
    return CB

def calcular_Zj(var_bas,arr,x,b,Cj):
    CB = obtener_CB(var_bas,x,Cj) #obtener cociente de las variables basicas en la FO
    Zj = np.zeros((1,x+1)) #matriz vacia con tamaño de las variables +1 que es b
    for i in range(x):
        #st.write(arr[:,i])
        Zj[0,i] = sum(x * y for x, y in zip(CB, arr[:,i]))
        #realiza la sumatoria de la multiplicacion entre el cociente basico con el valor del array
    #st.write(Zj)
    Zj[0,x] = sum(x * y for x, y in zip(CB, b))
    #realiza la sumatoria de la multiplicacion entre el cociente basico con el valor del b
    return Zj #retorno de Zj

def calcular_Zj_Cj(Zj,Cj,x):
    Zj_Cj = np.zeros((1,x))
    for i in range(x):
        #resta el valor de los valores de Zj con los cocientes de la FO
        Zj_Cj[0,i] = Zj[0,i] - Cj[0,i]
    return Zj_Cj

def graficar_tablero(var_bas,Cj,x,r,arr,b,Zj,Zj_Cj,base,co_min):
    tablero = '\n|'
    k=0
    for i in range(var_bas.size):
        if var_bas[0,i] == 1:
            tablero += f'{Cj[0,i]}|'
            tablero += f'$x_{{{i+1}}}$|'
            
            for j in range(x):
                if j == base or k == co_min[0,r]:    
                    tablero += f':red[{arr[k,j]}]|'  
                else:
                    tablero += f'{arr[k,j]}|'               
            tablero += f'{b[k]}|'
            tablero += f'{co_min[0,k]}|\n|'
            k+=1
    tablero += f'|$Z_j$|' 
    for i in range(x+1):
        tablero += f'{Zj[0,i]}|'
    tablero += f'\n||$Z_j-C_j$|'
    for i in range(x):
        tablero += f'{Zj_Cj[0,i]}|' 
    return tablero

def prueba_optimalidad(obj,Zj_Cj,x):
    #evaluamos el obj
    if obj == 'Maximizar':
    #si queremos max, todos los valores deben ser positivos
        for i in range(x):
            if Zj_Cj[0,i] < 0:
                return False #si alguno llega a ser negativo retorna que no es optima la solucion
        return True
    elif obj == 'Minimizar':
    #si queremos min, todos los valores deben ser negativos
        for i in range(x):
            if Zj_Cj[0,i] > 0:
                return False #si alguno llega a ser postivo retorna que no es optima la solucion
        return True

def seleccionar_base(obj,Zj_Cj,x):
    #variables de control
    base = -1 #no hay base
    mejor = 0 #variable que mas ayude al obj
    #evaluamos el objetivo
    if obj == 'Maximizar':
        for i in range(x):
            #buscamos la variable "mas negativa"
            if Zj_Cj[0,i] < mejor:
                mejor = Zj_Cj[0,i] #recorre buscando el mas negativo
                base = i #guarla la posicion de la mejor base
    elif obj == 'Minimizar':
        #buscamos la variable "mas positiva"
        for i in range(x):
            if Zj_Cj[0,i] > mejor:
                mejor = Zj_Cj[0,i] #recorre buscando el + positivo
                base = i #guarda posicion
    return base #retorna la posicion de la base

def cociente_minimo(b,arr,base,r):
    co_min = np.zeros((1,r+1)) #matriz vacia del tamaño de restricciones +1
    min = [999999999999999999,-1]
    #buscamos el >= 0 mas pequeño, asi que tomamos un gran valor, y variable de control para saber si se encontro cociente minimo
    for i in range(r):
        #st.write(b[i])
        co_min[0,i] = b[i] / arr[i,base] #divide b por el valor de la base seleccionada
        if co_min[0,i] >= 0 and co_min[0,i] < min[0]:
        #se evalua si el minimo es mayor o igual a 0 y si es menor que la variable de control
            min = [co_min[0,i],i] #guardamos el valor minimo encontrado
        #if co_min[0,i] == min[0]:
            #co_min[0,r] = -1
            #return co_min
    co_min[0,r] = min[1] #guardamos la posicion del cosciente minimo en la ultima parte de vector
    return co_min

def obtener_B_inv(A,var_bas,r,x):
    B = np.zeros((r,r)) #matriz de tamaño de restricciones
    k=0
    for i in range(x):
        if var_bas[0,i] == 1:
        #evalua si la variable es basica
            for j in range(r):
                #st.write(arr[j,i])
                #si lo es, usa la posicion de la variable para llenar con el valor en A
                B[j,k] = A[j,i]
            k+=1 #apuntador de columnas en matriz B
    #st.write('B',B)
    B_inv = np.linalg.inv(B) #sacar inversa a una matriz
    return B_inv

def crear_grafica(x_a,r,solucion,restricciones,b,option,factible,margen,FO_original,solucion_Z):
    if x_a == 2:
        u = np.zeros((r,))
        for i in range(r):
            if restricciones[i,0] == 0:
                u[i] = 1
            elif restricciones[i,1] == 0:
                u[i] = 2
        st.write('### Gráfica')
        puntos = 10
        fig, ax = plt.subplots()
        X = np.linspace(solucion[0,0]-margen,solucion[0,0]+margen,puntos)
        Y = np.zeros((puntos,))
        l = 0
        color_mapping = {
                '<=': 'blue',
                '=': 'green',
                '>=': 'red',
            }
        for i in range(r):
            for j in range(puntos):
                if u[i] == 0:
                    Y[j] = (b[i] - (restricciones[i,0]*X[j]))/restricciones[i,1]
                elif u[i] == 1:
                    Y[j] = (b[i])/restricciones[i,1]
                elif u[i] == 2:
                    Y[j] = (b[i])/restricciones[i,0]
            
            color = color_mapping.get(option[i], 'gray')
            if u[i] == 2:
                X_1 = np.linspace(solucion[0,0]-(margen*5),solucion[0,0]+(margen*5),puntos)
                ax.plot(Y,X_1,color=color)
                #st.write(np.linspace(Y[0],margen*100,puntos),(margen*100))
                if option[i] == '>=':
                    ax.fill_between(np.linspace(Y[0],margen*100,puntos), (margen*100),-(margen*100), color='red', alpha=0.15)
                elif option[i] == '<=':
                    ax.fill_between(np.linspace(-margen*100,Y[0],puntos), (margen*100),-(margen*100), color='blue', alpha=0.15)
                
            else:
                if option[i] == '<=':
                    # Sombreamos desde Y hasta menos margen*100
                    ax.fill_between(X, Y, -(margen*100), color='blue', alpha=0.15)
                elif option[i] == '>=':
                    #Sombreamos desde margen*100 hasta Y
                    ax.fill_between(X, (margen*100), Y, color='red', alpha=0.15)
                ax.plot(X,Y,color=color)
            #st.write(b[i],restricciones[i,0],restricciones[i,1])
        if factible:
            X = np.linspace(solucion[0,0]-(margen*0.8),solucion[0,0]+(margen*0.8),puntos)
            for i in range(puntos):
                if FO_original[0,0] == 0:
                    Y[i] = solucion_Z/FO_original[0,1]
                elif FO_original[0,1] == 0:
                    Y[i] = solucion_Z/FO_original[0,0]
                else:
                    Y[i] = (solucion_Z-FO_original[0,0]*X[i])/FO_original[0,1]
            if FO_original[0,1] == 0:
                X_1 = np.linspace(solucion[0,0]-(margen*1.1),solucion[0,0]+(margen*0.7),puntos)
                ax.plot(Y,X_1,color='brown')
            else:
                ax.plot(X,Y,color='brown')
            ax.plot(solucion[0,0],solucion[0,1],marker='o', markersize=5, color='black')
        ax.set_xlabel('$x_1$')
        ax.set_ylabel('$x_2$')
        
        ax.set_xlim(solucion[0,0] - margen, solucion[0,0] + margen)
        ax.set_ylim(solucion[0,1] - margen, solucion[0,1] + margen)

        # Resaltar el eje x (horizontal)
        ax.axhline(0, color='black', linewidth=1)
        
        # Resaltar el eje y (vertical)
        ax.axvline(0, color='black', linewidth=1)
        ax.grid(True)
        st.pyplot(fig)
               

if __name__ == '__main__':
    main()

