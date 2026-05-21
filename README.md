# Green Computing Project

Questo progetto implementa una pipeline di classificazione binaria su dati derivati da cartelle cliniche elettroniche (EHR), misurando le performance e il consumo energetico attraverso [CodeCarbon](https://github.com/mlco2/codecarbon). La pipeline viene eseguita su **tutti e 5 i dataset** forniti.

## Struttura del Progetto

```
green-computing-project/
├── five_EHRs_public_datasets/   # I 5 dataset CSV (target = ultima colonna)
├── results/                     # Output: MCC e metriche per ogni dataset
│   ├── base_results.csv
│   ├── optimized_results.csv
│   └── r_results.csv
├── main_base.py                 # Script 1: baseline Python (RandomForest, 100 alberi)
├── main_optimized.py            # Script 2: Python ottimizzato (30 alberi, max_depth=5, n_jobs=-1)
├── main_r.R                     # Script 3: versione R ottimizzata (eseguita via Docker)
├── main_r_wrapper.py            # Wrapper Python per misurare le emissioni dello script R
├── plot_results.py              # Genera i grafici comparativi per il report
├── Dockerfile                   # Immagine Docker per eseguire main_r.R
├── emissions_base.csv           # Output CodeCarbon: script baseline
├── emissions_ottimizzato.csv    # Output CodeCarbon: script ottimizzato
├── emissions_r.csv              # Output CodeCarbon: script R
├── run_base.sh                  # Esegue main_base.py
├── run_optimized.sh             # Esegue main_optimized.py
├── run_r.sh                     # Builda il container Docker ed esegue main_r.R
└── run_all.sh                   # Esegue tutti e tre gli script in sequenza
```

## Requisiti

### Python
- Python 3.9+
- Dipendenze:

```bash
pip install scikit-learn codecarbon pandas numpy
```

### R (tramite Docker)
- [Docker](https://www.docker.com/) installato e in esecuzione

## Istruzioni per l'Esecuzione

Prima di eseguire gli script Bash, assicurati che abbiano i permessi di esecuzione:

```bash
chmod +x run_*.sh
```

### Eseguire i Modelli Singolarmente

- **Script 1 — Python Baseline:**
  Avvia il modello non ottimizzato (`main_base.py`) su tutti e 5 i dataset:
  ```bash
  ./run_base.sh
  ```

- **Script 2 — Python Ottimizzato:**
  Avvia il modello ottimizzato (`main_optimized.py`) su tutti e 5 i dataset:
  ```bash
  ./run_optimized.sh
  ```

- **Script 3 — R via Docker:**
  Builda l'immagine Docker ed esegue `main_r.R` su tutti e 5 i dataset:
  ```bash
  ./run_r.sh
  ```

### Eseguire Tutto Insieme

Per eseguire l'intera pipeline in sequenza automatica (Baseline → Ottimizzato → R):

```bash
./run_all.sh
```

### Generare i Grafici

Dopo aver eseguito tutti gli script, genera i grafici comparativi per il report:

```bash
python plot_results.py
```

## Risultati

Al termine delle esecuzioni, nella cartella `results/` troverai:

| File | Contenuto |
|------|-----------|
| `base_results.csv` | MCC medio e std per ogni dataset — script baseline |
| `optimized_results.csv` | MCC medio e std per ogni dataset — script ottimizzato |
| `r_results.csv` | MCC medio e std per ogni dataset — script R |

Nella root del progetto troverai inoltre i file `emissions_*.csv` generati da CodeCarbon con le misure di **Wh**, **CO₂-eq (grammi)** e **secondi** per ogni script.

## Metodologia

- **Classificatore**: RandomForest
- **Validazione**: Repeated Hold-Out con 100 iterazioni (seed variabile `random_state=i`)
- **Test size**: 20% del dataset ad ogni iterazione
- **Metrica**: Matthews Correlation Coefficient (MCC)
- **Misura energetica**: [CodeCarbon](https://github.com/mlco2/codecarbon) con `country_iso_code="ITA"`
- **Dataset**: 5 dataset EHR pubblici in formato CSV — target sempre nell'ultima colonna

## Ottimizzazioni applicate (Script 2 e 3)

- Riduzione del numero di alberi: da 100 a 30 (`n_estimators=30`)
- Limitazione della profondità massima: `max_depth=5`
- Parallelizzazione su tutti i core disponibili: `n_jobs=-1`
- Rimozione delle feature a varianza zero prima del loop (`VarianceThreshold`)