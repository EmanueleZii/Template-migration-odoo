## Template o script pronti per migrations su odoo

La struttura delle cartelle
Odoo cerca automaticamente gli script di migrazione in una cartella specifica all'interno del tuo modulo. La struttura deve essere:

mio_modulo/migrations/VERSIONE/pre-migrate.py o post-migrate.py

VERSIONE: Deve corrispondere alla versione nel file __manifest__.py (es. 19.0.1.0).

pre-migrate.py: Eseguito prima del caricamento del modulo (utile per rinominare colonne o tabelle).

post-migrate.py: Eseguito dopo il caricamento (utile per trasformare dati complessi usando i modelli Odoo).
