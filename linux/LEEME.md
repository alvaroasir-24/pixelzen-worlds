# PixelZen para Linux (GNOME Shell 46–50+)

Extensión de GNOME Shell con fondo pixel art animado que sigue la posición solar real (o simulada) y panel HUD opcional.

## Instalación

```bash
cd linux
./instalar.sh                             # tema por defecto (fittoa)
./instalar.sh --tema=continente-demoniaco # instalar directamente el Continente Demoníaco
./instalar.sh --90m                       # activar ciclo de 24 h en 90 min
```

## Cambiar de fondo (escalable)

```bash
./tema.sh --listar
./tema.sh fittoa
./tema.sh continente-demoniaco
./tema.sh hunter-x-hunter
./tema.sh black-clover
./tema.sh spiderman-miles-morales
```

## Control de hora y ciclo

```bash
./hora.sh 90m     # ciclo completo de 24 horas en 90 minutos
./hora.sh real    # hora real del reloj
./hora.sh demo    # ciclo rápido de 24 horas en 90 segundos
./hora.sh 21:30   # congela el paisaje a una hora fija
```

## Desinstalar

```bash
./desinstalar.sh
```
