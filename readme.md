# Fantascienza.com Book Catalog
[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)   

Vedi l'elenco [online](http://mte90.tech/fantascienza.com-book-catalog/)!

Il progetto nasce come sostituto alla ricerca e filtri del portale [Fantascienza.com](https://fantascienza.com/) e probabilmente funziona anche sugli altri siti del network.

Non è possibile cercare libri o autori perchè la ricerca avviene su tutto, compreso gli articoli e non è precisa.  
Esempi: 

* Beam Piper: è un autore ma siccome ha Piper nel nome si trovano gli episodi di Doctor Who con una attrice dallo stesso cognome
* Ciclo fondazione: è una serie di libri di Asimov ma trova tutti gli articoli con il termine `ciclo`, 322 per essere precisi e 51 approfondimenti

Il programma quindi cerca tutte le pagine che sono schede di libri partendo dalla [prima](https://www.fantascienza.com/1006/blu-profondo) e arrivando all'ultimo articolo. Non essendo possibile avere una pagina archivio di sole schede l'unica è leggere **ogni singola pagina e passare alla successiva**.  
Vista la mole di pagine da controllare il database parte dall'ultima esecuzione per l'aggiornamento e cerca nuove schede.

I dati estrapolati sono salvati in un file JSON contente le informazioni del libro (non sempre sono tutte disponibili specialmente per le vecchie schede) e per ogni autore associa l'articolo/id della scheda.

Successivamente viene generato un indice HTML navigabile per autore con tutti i link alle schede. Basta usare la ricerca del browser con `Ctrl+f`.

L'elenco è aggiornato **settimanalmente** in automatico.