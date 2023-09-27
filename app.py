import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def main():
    st.set_page_config(
        page_title="Método Simplex",
        page_icon="🤖"
    )
    # Página incial
    st.title('Método simplex')
    
    # Selección del método
    st.selectbox('Método',('Penalización (Gran M)','Dos fases'))
    
    ## Entrada de número de variables y restricciones
    x = st.number_input('Inserte número de variables',min_value=1)
    r = st.number_input('Inserte número de restricciones', min_value=1)
    
    # Selección de objetivo (Maximizar o Minimizar)    
    obj = st.selectbox('¿Cuál es el objetivo de la función?', ('Maximizar','Minimizar'))
    
    # Entrada de la función objetivo    
    st.write('### Función Objetivo')
    FO = np.empty((1, x))
    col_FO = st.columns(x, gap='small')
    for j in range(0, x):
        FO[0,j] = col_FO[j].number_input(f'$x_{{{j+1}}}$', key=f'col_FO{j}')
    
    # Entrada de restricciones    
    col = []
    option = []
    rest = []
    arr = np.empty((r, x))
    k=0
    for i in range(0,r):
        st.write(f'#### Restricción {i+1}')
        col.append(st.columns(x + 2, gap='small'))
        for j in range(0, x):
            arr[i,j] = col[i][j].number_input(f'$x_{{{j+1}}}$', key=k)               
            k+=1
        option.append(col[i][x].selectbox('',('<=', '=', '>='), key=k))
        rest.append(col[i][x+1].number_input('', key=k+1))            
        k+=2
        
    # Botón para continuar con el método simplex        
    if st.button("Continuar",key='boton1'):
        metodo_simplex(x,r,obj,FO,arr,option,rest)
        
def metodo_simplex(x,r,obj,FO,arr,option,rest):
    
    x_a = x
    restricciones = arr.copy()
    
    # Inicialización de variable M en función del objetivo    
    if obj == 'Maximizar':
        M = -999999999999
    elif obj == 'Minimizar':
        M = 999999999999
    
    #Estandarizar
    x,r,FO,arr,option,rest = estandarizar(x,r,FO,arr,option,rest,M)
    
    # Mostrar estandarizado  
    st.write('### Estandarizado')
    st.write('##### Función objetivo')
    
    # ... Código para mostrar la función objetivo y restricciones estandarizadas
    texto_FO = f'${obj}$ $Z ='
    for i in range(x-1):
        if FO[0,i+1] >= 0:
            texto_FO += f'{FO[0,i]}x_{{{i}}}+'
        else:
            texto_FO += f'{FO[0,i]}x_{{{i}}}'
    texto_FO += f'{FO[0,x-1]}x_{{{x-1}}}$'
    st.write(texto_FO)
    
    st.write('##### Restricciones')
    for i in range(r):
        texto_r = f'{i+1}. $'
        for j in range(x-1):
            if arr[i,j+1] >= 0:
                texto_r += f'{arr[i,j]}x_{{{j}}}+'
            else:
                texto_r += f'{arr[i,j]}x_{{{j}}}'
        texto_r += f'{arr[i,x-1]}x_{{{x-1}}}={rest[i]}$'
        st.write(texto_r)
        
    # Preparar tablero inicial
    var_bas,Cj,b,A,k,tablero = preparar_tablero(x,x_a,r,obj,FO,arr,option,rest,M)
    if k == 0:
        st.write('No hay variables basicas')
        return 
    b_r = b.copy()

    # Bucle para aplicar el método simplex
    h = 0
    opt_encontrado = False
    while True:
    #for p in range(5):
        if h > 10000:
            tablero = 'No se puede obtener una solución optima'
            st.write(tablero)
            break
        Zj = np.round(calcular_Zj(var_bas,arr,x,b_r,Cj),14)
        #st.write('Zj',Zj)
        Zj_Cj = np.round(calcular_Zj_Cj(Zj,Cj,x),14)
        #st.write('Zj_Cj',Zj_Cj)
        
        base = seleccionar_base(obj,Zj_Cj,x)
        #st.write('base',base)
        co_min = np.round(cociente_minimo(b_r,arr,base,r),10)
        #st.write('co_min',co_min)
        tablero += graficar_tablero(var_bas,Cj,x,r,arr,b_r, Zj,Zj_Cj, base,co_min)        
        
        if prueba_optimalidad(obj,Zj_Cj,x) == True:
            st.write(tablero)
            opt_encontrado = True
            break
           
        ## Cambio de base
        #st.write(var_bas)
        k=0
        for i in range(x):
            if var_bas[0,i] == 1:
                if k == co_min[0,r]:
                    var_bas[0,i] = 0
                    var_bas[0,base] = 1
                    break
                else:
                    k += 1
        #st.write('var_bas',var_bas)                
        
        B_inv = obtener_B_inv(A,var_bas,r,x)
        #st.write('B_inv',B_inv)
        #st.write('A',A)
        #st.write('b',b)
        arr = np.round(np.dot(B_inv,A),14)
        b_r = np.round(np.dot(B_inv,b),14)
        
        #st.write(arr)
        h += 1
    
    if opt_encontrado:
        if Zj[0,x] < 0:
            st.write('No se pudo encontrar la solución optima')
            return
        st.write('### Solución optima')
        st.write(f'$Z = {Zj[0,x]}$')
        m = 0
        solucion = np.zeros((1,x_a))
        for i in range(x_a):
            if var_bas[0,i] == 1:
                st.write(f'$x_{{{i+1}}}={b_r[m]}$')
                solucion[0,i] = b_r[m]
                m+=1
            else:
                st.write(f'$x_{{{i+1}}}=0$')
                solucion[0,i] = 0
        crear_grafica(x_a,r,solucion,restricciones,b,option)
        
    
def estandarizar(x,r,FO,arr,option,rest, M):
    # Cambio de signo cuando el lado derecho es negativo
    for i in range(r):
        if rest[i] < 0:
            rest[i] = rest[i]*-1
            arr[i] = arr[i]*-1
            if option[i] == '<=':
                option[i] = '>='
            elif option[i] == '>=':
                option[i] = '<='    
    
    # Cantidad de variables que agregaremos
    var_agr = x
    art = 0
    for o in option:
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
    a[:,:x] = arr
    var_art = np.zeros((1,art))
    #st.write(var_art)
    var_art_i = 0
    columna = 0
    for i in range(r):
        for j in range(x+i):
            if option[i] == '<=':
                a[i,x+columna]=1
                break
            elif option[i] == '=':
                a[i,x+columna]=1
                var_art[0,var_art_i] = x+columna
                var_art_i += 1
                break
            elif option[i] == '>=':
                a[i,x+columna]=-1
                a[i,x+columna+1]=1
                var_art[0,var_art_i] = x+columna+1
                var_art_i += 1
                columna += 1
                break
        columna += 1
    #st.write(a)
    arr = a
    
    #Estandarizamos la FO
    b = np.zeros((1,var_agr))
    b[:,:x] = FO
    
    FO = b
    x = var_agr
    #st.write(var_art)
    for i in range(art):
        FO[0,int(var_art[0,i])] = M

    #st.write(FO)
    
    return x,r,FO,arr,option,rest  
    
def preparar_tablero(x,x_a,r,obj,FO,arr,option,rest,M):
    Cj = FO
    b = rest
    A = arr
    
    #Determinar las basicas
    var_bas = np.zeros((1,x))
    for i in range(x):
        k = 0
        for j in range(r):  
            if i <= x_a-1:
                break          
            if arr[j,i] != 0 and arr[j,i] != 1:
                k = 99
                break
            elif arr[j,i] == 1:
                k += 1
        if k == 1:
           var_bas[0,i] = 1
    
    k=0
    for v in var_bas:
        if (v == 1).any():
            k+=1
            
    tablero = ''
    if k == 0:
        return var_bas, Cj, b, A, 0,tablero
    else:
        ## Graficación de tablero
        st.write('### Tablero')
        tablero = f'| | $C_j$ |'
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
        return var_bas, Cj,b,A,1,tablero

def obtener_CB(var_bas,x,Cj):
    CB = []
    for i in range(x):
        if var_bas[0,i] == 1:
            CB.append(Cj[0,i])            
    #st.write(CB)
    return CB

def calcular_Zj(var_bas,arr,x,b,Cj):
    CB = obtener_CB(var_bas,x,Cj)
    Zj = np.zeros((1,x+1))
    for i in range(x):
        #st.write(arr[:,i])
        Zj[0,i] = sum(x * y for x, y in zip(CB, arr[:,i]))
    #st.write(Zj)
    Zj[0,x] = sum(x * y for x, y in zip(CB, b))
    return Zj

def calcular_Zj_Cj(Zj,Cj,x):
    Zj_Cj = np.zeros((1,x))
    for i in range(x):
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
    if obj == 'Maximizar':
        for i in range(x):
            if Zj_Cj[0,i] < 0:
                return False
        return True
    elif obj == 'Minimizar':
        for i in range(x):
            if Zj_Cj[0,i] > 0:
                return False
        return True

def seleccionar_base(obj,Zj_Cj,x):
    base = -1
    mejor = 0
    if obj == 'Maximizar':
        for i in range(x):
            if Zj_Cj[0,i] < mejor:
                mejor = Zj_Cj[0,i]
                base = i
    elif obj == 'Minimizar':
        for i in range(x):
            if Zj_Cj[0,i] > mejor:
                mejor = Zj_Cj[0,i]
                base = i
    return base

def cociente_minimo(b,arr,base,r):
    co_min = np.zeros((1,r+1))
    min = [999999999999999999,-1]
    for i in range(r):
        #st.write(b[i])
        co_min[0,i] = b[i] / arr[i,base]
        if co_min[0,i] >= 0 and co_min[0,i] < min[0]:
            min = [co_min[0,i],i]
    co_min[0,r] = min[1]
    return co_min

def obtener_B_inv(A,var_bas,r,x):
    B = np.zeros((r,r))
    k=0
    for i in range(x):
        if var_bas[0,i] == 1:
            for j in range(r):
                #st.write(arr[j,i])
                B[j,k] = A[j,i]
            k+=1
    #st.write('B',B)
    B_inv = np.linalg.inv(B)
    return B_inv

def crear_grafica(x_a,r,solucion,restricciones,b,option):
    if x_a == 2:
        u = np.zeros((r,))
        for i in range(r):
            if restricciones[i,0] == 0:
                u[i] = 1
            elif restricciones[i,1] == 0:
                u[i] = 2
        st.write('### Gráfica')
        margen = 1
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
                margen=5
                X = np.linspace(solucion[0,0]-margen,solucion[0,0]+margen,puntos)
                ax.plot(Y,X,color=color)
                margen=1
                X = np.linspace(solucion[0,0]-margen,solucion[0,0]+margen,puntos)
            else:
                ax.plot(X,Y,color=color)
            #st.write(b[i],restricciones[i,0],restricciones[i,1])
        ax.plot(solucion[0,0],solucion[0,1],marker='o', markersize=5, color='black')
        ax.set_xlabel('$x_1$')
        ax.set_ylabel('$x_2$')
        ax.grid(True)
        st.pyplot(fig)
               

if __name__ == '__main__':
    main()

