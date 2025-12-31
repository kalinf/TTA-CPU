## Must have
- generowanie rdzenia z konfiguracji
    - ~~generate_template.py~~
        - ~~przyjęcie ścieżki do katalogu z konfiguracją~~
        - ~~wygenerowanie katalogu FU z miejscem w plikach na uzupełnianie własnych funkcjonalności~~
        - ~~nadpisanie adresów / zapisanie ich w nowym pliku konfiguracyjnym~~
        - ~~wyliczenia layoutów i magistral~~
    - ~~zainstancjonowanie layoutów i magistral~~
    - ~~zaimportowanie konstruktorów jednostek funkcyjnych i ich instancjonowanie~~
- ~~test wyliczanie n-tej liczby fibbonacciego~~
    - ~~pierwszy działający test~~
    - ~~ogarnięcie pytest~~
    - ~~tłumaczenie czytelnych transportów (Adder.i0 -> Result.trigger) na "assembler"~~
- ~~brak operacji nie zmieniający stanu~~
    - ~~przydzielanie rejestrów od 1~~
- ~~porty inout~~
- ~~fix: poprawne przydzielanie portów~~
- porządne komentarze
- ~~pamięć programu~~
- pamięć danych
- ~~logical operations unit~~
- ~~instruction operation fu~~
- ~~uniwersalne tesy "assemblerowe"~~
- testy uruchamiane na FPGA
    - ~~zdobycie (drogą kupna lub wypożyczenia) devkitu FPGA~~
    - ~~synteza na ecp5~~
    - ~~testy timingów~~
    - uruchomienie na sprzęcie
    - możliwość zapisywania pamięci bez konieczności resyntezowania rdzenia
- Licencja i przeklejone notki licencyjne z miejsc skąd brałam kod (colorlight i9, coreblocks)
- PLL żeby mieć faktycznie fajniejszą częstotliwość niż 12 MHz
- ~~Indirect unit~~ 

## Nice to have
- częściowo pipelined TTA
- ~~formatter~~
- pyproject.toml
- wiele możliwych szyn danych ("przerwania" między jednostkami)
- ~~pisanie pseudo assemblera z wykorzystaniem niekoniecznie instancji rdzenia (lepiej pliku konfiguracyjnego)~~
- automatyczne wykrywanie Fmax i dostrajanie PLL pod ten Fmax (jest program który wylicza dla pll na ecp5)

## Optional
- ~~UART~~
- wiele możliwych szyn instrukcji (VLIV)


co przed wtorkiem [hehe na pewno]:
- ~~budowanie "assembly" nie z dut obiektu rdzenia a z obiektu stworzonego z pliku konfiguracyjnego (same adresy)~~
- ~~indirect unit~~
- ~~przykład lepszego fetchera dla fibonacciego i test lepszy fibonacciego~~
- ~~przygotowanie zestawienia, co robili inni (wielocyklowość, operowanie na pamięci)~~
- pamięć programu
- ~~żeby się i syntezowało i pytestowało~~
- ~~procedury obsługi przerwań i reakcja na zdarzenia zewnętrzne~~
- obsługa wielu przerwań
- stos i obsługa zapisania stanu przy wejściu do handlera przerwań
- ~~uruchamianie różnych testów dla różnych rdzeni~~
- ~~przekazywanie resources~~
- ~~"mockowanie" resources dla symulacji~~
- ograniczanie zasobów przekazywanych do jednostek???
- subsignals w resources config i piny io
- pll
- pythonowy pseudo-assembler <--> json <--> plik binarny
- ~~osobne miejsce na ip cores niebędące fu~~
- synchronizować domyślnie inputy??? jeżeli, to wypadałoby W JEDNYM MIEJSCU a nie w każdym fu
- popraw skrypt formatujący
- usunąć init z base_asm_test

co potem:
- bootloader, programowanie pamięci bez wgrywania rdzeni (jak to z tą pamięcią co jest layoutem)
- częściowo pipelined [NIE ZDĄŻĘ, ODPADA]
- wiele możliwych szyn instrukcji (VLIV)
- wiele możliwych szyn danych (przerwania między jednostkami)
- ~~komunikacja z komputerem~~

pytania
- programowanie pamięci bez wgrywania rdzeni (jak to z tą pamięcią co jest layoutem)
- czy regenerować pliki fu przy ponownym generowaniu rdzenia
- ~~co z pytest i testami dla konkretnych konfiguracji~~