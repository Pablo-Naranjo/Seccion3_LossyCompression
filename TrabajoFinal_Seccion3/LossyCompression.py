from PIL import Image, ImageOps
from matplotlib import pyplot as plt
import os
import warnings
warnings.filterwarnings("error")


def graficar(datos, nombre, f):
    x = range(len(datos))
    ax = plt.subplot(2, 1, f)
    plt.xticks([0, 50, 100, 150, 200, 255], [0, 50, 100, 150, 200, 255])
    ax = plt.bar(x, datos, align='center')
    plt.title('Histograma ' + nombre)
    plt.xlabel('Valores de intensidad')
    plt.ylabel('Numero de pixeles')

    return None


fig = plt.figure(figsize=(9, 6))

nombre = 'imagen'
formato = '.jpg'

for i in range(1, 2):
    # abrir la imagen
    ruta = nombre + str(i) + formato
    print(ruta)
    im1 = Image.open(ruta)

    # posterizar la imagen
    if im1.mode != 'L':
        im1 = im1.convert('L')
    im2 = ImageOps.posterize(im1, 7)
    im1.show()
    im2.show()

    # obtener el histograma de la imagen original
    titulo = nombre + str(i) + ' original'
    historgrama1 = im1.histogram()
    graficar(historgrama1, titulo, 1)

    # obtener el histograma de la imagen posterizada
    titulo = nombre + str(i) + ' posterizada'
    historgrama2 = im2.histogram()
    graficar(historgrama2, titulo, 2)

    # mostrar los histogramas
    plt.show()      # ES NECESARIO CERRAR LA VENTANA DE LOS HISTOGRAMAS PARA CONTINUAR

    # guardar las imagenes posterizadas
    im2.save(nombre + str(i) + 'posterizada' + formato)
    im1.close()

    # compactar la imagenes posterizadas
    im1 = Image.open(nombre + str(i) + 'posterizada' + formato)
    width, height = im1.size

    try:
        im1 = im1.resize((width, height), Image.ANTIALIAS)
        im1.save(nombre + str(i) + 'comprimida' + formato)
    except DeprecationWarning:
        print('')
    else:
        print('')

    im1.close()

    # obtener el código F26 de las imagenes posterizadas
    im1 = Image.open(nombre + str(i) + 'posterizada' + formato)
    datos = list(im1.getdata())

    # convertir la lista en una matriz
    M = [datos[width*a : width*(a+1)] for a in range(height)]
    x = 0
    y = 0
    t = 0
    AuxVar = 0
    cf26 = []
    band = False

    while x < (width - 1):
        y = t
        while y < height:
            t = 0
            band = False
            if M[x][y] > AuxVar:
                AuxVar += 1
                cf26.append('Y')
            elif M[x][y] == AuxVar:
                if (AuxVar - M[x][y+1]) >= 2:
                    AuxVar -= 1
                    cf26.append('Z')
                elif (AuxVar - M[x][y+1]) == 1:
                    AuxVar -= 1
                    cf26.append('Q')
                elif AuxVar < M[x][y+1]:
                    AuxVar += 1
                    cf26.append('I')
                elif AuxVar == M[x][y+1]:
                    cf26.append('A')
                if (AuxVar - M[x+1][y]) == 1 or (AuxVar - M[x+1][y]) == 2:
                    AuxVar -= 1
                    cf26.append('Z')
                elif (AuxVar - M[x+1][y]) == 1:
                    AuxVar -= 1
                    cf26.append('W')
                    t = y
                    band = True
                elif AuxVar < M[x+1][y]:
                    AuxVar += 1
                    cf26.append('G')
                    t = y
                    band = True
                elif AuxVar == M[x+1][y]:
                    AuxVar -= 1
                    cf26.append('O')
                    t = y
                    band = True
            y += 1

            if band == True:
                x += 1
                break
            else:
                continue
        x += 1

    F26 = ''.join(cf26)
    print(f'F26 {nombre}{str(i)}: {F26}')

    im1.close()
    im2.close()

    # calcular el error cometido entre la imagenes posterizadas
    # y compactadas con la imagen original

    # información de la imagen original
    img_original = Image.open(nombre + str(i) + formato)
    if img_original.mode != 'L':
        img_original = img_original.convert('L')
    datos1 = list(img_original.getdata())
    M_original = [datos1[width*a : width*(a+1)] for a in range(height)]

    # información de la imagen comprimida
    img_comprimida = Image.open(nombre + str(i) + 'comprimida' + formato)
    datos2 = list(img_comprimida.getdata())
    M_comprimida = [datos2[width * a: width * (a + 1)] for a in range(height)]

    cont = 0
    for x in range(width):
        for y in range(height):
            if M_original[x][y] != M_comprimida[x][y]:
                cont += 1

    total = width * height
    p_error = cont * 100 / total

    print(f'El porcentaje de error de la imagen {str(i)} con su imagen comprimida es {p_error:.2f}%')
    img_original.close()
    img_comprimida.close()

    img_original = Image.open(nombre + str(i) + formato)
    img_original.save(nombre + str(i) + '_.jpeg')
    size1 = os.stat(nombre + str(i) + '_.jpeg').st_size

    size2 = os.stat(nombre + str(i) + 'comprimida' + formato).st_size

    razon = size1/size2
    print(f'La razón de compresión respecto a JPEG de la imagen {i} es: {razon:.5f}')

    img_original.close()
