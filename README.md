# Colisiones-y-l-gica-de-juego

Manual Tecnico
Arquitectura del Juego
blob: representa al jugador y a los bots. Contiene posición, masa, velocidad, color, movimiento y radio.


food: representa la comida que los Jugadores y bots pueden consumir para crecer.


game: controla la lógica principal, el ciclo de juego, la actualización de jugadores/bots, la cámara y el renderizado.


Ciclo principal (run):


Captura eventos del teclado y mouse.


Actualiza posiciones de jugadores y bots.


Detecta colisiones con comida y entre jugadores/bots.


Dibuja todos los elementos en pantalla.


Actualiza la cámara y la interfaz de usuario.



Cámara
La cámara sigue al jugador promedio (o única célula del jugador).


Posición de la cámara (camx, camy) calculada como:

 camx = clamp(promedio_x - WIDTH/2, 0, WORLD_W - WIDTH)
camy = clamp(promedio_y - HEIGHT/2, 0, WORLD_H - HEIGHT)

Sirve para pasar las coordenadas del mundo a la pantalla, y así dibujar la cuadrícula, las manchas y la comida tomando en cuenta dónde está la cámara.

Colisiones
Jugador-comida: círculo vs círculo. Si la distancia entre centros < suma de radios, el jugador gana masa proporcional al tamaño de la comida.


Jugador-bot: círculo vs círculo. Si la masa del jugador > 1.15× masa del bot y colisionan, el bot muere y el jugador gana parte de su masa.


Bot-jugador: Si un robot es mucho más grande que tú y chocan, se acaba el juego.

Split y merge:Tras dividirse, las células del jugador pueden juntarse si pasan 6 segundos y chocan suavemente.




 Inteligencia Artificial (IA)
Cada bot calcula:


Amenaza: si hay otro bot mayor cercano, huye.


Presas: si hay un bot más pequeño, lo persigue.


Movimiento aleatorio: si no hay amenaza ni presa, se mueve hacia un punto aleatorio dentro del mundo.


Los bots usan velocidad proporcional a su tamaño:

 speed = max(60, 260 / (1 + 0.04 * r))

Parámetros y Balance
Parámetro
Valor / Fórmula
Descripción
Masa inicial jugador
600
Tamaño de partida
Masa mínima para split
400
No permite dividir si es menor
Tiempo para fusionar
6 s
Después de split, las células se fusionan
Masa perdida al dash
5%
Al usar dash con espacio
Masa perdida al eject
3%
Al expulsar masa con E
Velocidad base blobs
260
Ajustada por radio
Cantidad inicial comida
1000
Generada aleatoriamente
Cantidad bots
10–18
Generados con masa aleatoria


Balance:


Se busca que los jugadores puedan crecer al comer comida y bots más chicos.
Los bots grandes son un problema porque impiden que los jugadores mejoren muy rápido.
Echar masa y dividirse añade ideas para que pienses bien cómo aguantar.



Interfaz y Controles
Mouse: mover el jugador.


Q: dividir la célula en 2.


E: expulsar masa.


R: reiniciar partida.


ESC: salir del juego.


Interfaz muestra masa total y guía de controles.






Manual de Usuario – Mini Agar.io en Pygame
Requisitos e Instalación
Python 3.10 o superior instalado en tu computadora.


Pygame 2.x instalado.


Sistema operativo: Windows, macOS o Linux.





Controles
Tecla / Acción
Descripción
Mouse 
         Mover la célula principal.
Q
         Dividir la célula en 2 células (fusionan tras 6 s).
E
         Expulsar masa delante del jugador.
R
         Reiniciar partida.
ESC
         Salir del juego.

Objetivo del juego
Crecer consumiendo la comida y bots más pequeños.


Evitar a los bots más grandes.


Sobrevivir y derrotar a todos los bots para ganar.





Solución de problemas frecuentes (que verdaderamente pasaron)
Problema
Solución
ModuleNotFoundError: No module named 'pygame'
Instala Pygame usando pip install pygame.
El juego no se abre o se cierra inmediatamente
Asegúrate de estar ejecutando Python 3.10+ y que colicines.py esté en la carpeta actual.
Error al mover el jugador
Asegúrate de usar la ventana activa y el mouse dentro de la ventana del juego.
Error al expulsar masa (AttributeError)
Usa la versión actualizada del código con vx y vy en la clase food.
Juego muy lento
Cierra otros programas, reduce la cantidad de bots o comida en reset() para mejorar FPS.


