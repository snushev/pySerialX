![SerialX Icon](banner.png)

# PySerialX

Una libreria Python potente e intuitiva per controllare schede Arduino tramite comunicazione seriale.

## Cos'è PySerialX?

PySerialX è una libreria Python che fornisce un'interfaccia semplice e robusta per comunicare con schede Arduino via porta seriale. Permette di eseguire script nel linguaggio SerialX e di interagire con le variabili Arduino direttamente da Python.

## A cosa serve?

PySerialX è ideale per:

- **Controllo Arduino da Python**: Leggi e scrivi variabili su schede Arduino direttamente da Python
- **Esecuzione di script SerialX**: Interpreta e esegue script scritti nel linguaggio SerialX con compilazione JIT
- **Integrazione completa**: Integra facilmente i tuoi progetti Arduino nei workflow Python
- **Comunicazione affidabile**: Gestisce automaticamente la comunicazione seriale con threading e buffering
- **Prototipazione rapida**: Sviluppa soluzioni Arduino + Python in modo veloce e efficiente

## Caratteristiche principali

✨ **Compilazione JIT** - Interpretazione e compilazione Just-In-Time degli script SerialX  
📡 **Comunicazione asincrona** - Threading automatico per la lettura dei dati seriali  
🔢 **Tipi supportati** - Gestione di int, float e string  
🐍 **API Pythonica** - Interfaccia intuitiva e facile da usare  
⚡ **Performance** - Ottimizzazione del codice per comunicazioni seriali veloci  

## Installazione

```bash
pip install pyserialx @ http://github.com/SerialXProject/pySerialX/releases/latest/download/pyserialx.whl
```

## Utilizzo rapido

```python
from pySerialX import SerialX

# Connetti ad Arduino
device = SerialX(port='COM3', baud_rate=9600)

# Leggi una variabile da Arduino
value = device.get(int, 'temperatura')

# Scrivi una variabile su Arduino
device.set(int, 'setpoint', 25)
```

## Linguaggio SerialX

**SerialX** è un linguaggio di programmazione specializzato progettato specificamente per la comunicazione efficiente con microcontrollori Arduino. È optimizzato per:

- **Sintassi leggera**: Comandi semplici e diretti per il controllo dei dispositivi
- **Basso overhead**: Minimizza l'utilizzo di memoria sui dispositivi embedded
- **Comunicazione rapida**: Protocollo ottimizzato per la trasmissione seriale
- **Compatibilità universale**: Funziona su tutte le schede Arduino e compatibili

## SerialX_JIT: Compilazione Just-In-Time ad alte performance

**SerialX_JIT** è il motore di compilazione Just-In-Time che alimenta PySerialX. Offre:

- **Comunicazione più veloce**: Ottimizza la trasmissione dei dati via seriale
- **Interprete Arduino più leggero**: Riduce il carico computazionale sulla scheda Arduino

## Documentazione completa

Per una documentazione completa, esempi dettagliati e guide avanzate, visita:

📖 **[http://pasqualo.local:3001](http://SerialXProject.github.io/serialx-docs)**

## Versione

PySerialX v1.0.4 - Con supporto per integrazione Python completa
