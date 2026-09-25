# Devastace MB03+ 1.0

První číslované vydání naší úpravy pracovní verze Devastace pro MB03+.

## Použití

Soubor `runable/MBDEVMB03\_v1\_0.3` má 7168 bajtů a načítá se na adresu `#4000` (`#4000–#5BFF`). Nepotřebuje ZX ROM.

* Klávesa **Y** mění číslo stránky SRAM ve spodní oblasti (0-16383), zvolené číslo je zobrazeno vpravo na spodním řádku. 
* Číslo stránky zadávej v aktuálně zvolené soustavě (`0–255` nebo `00–FF`). Zapisuje se celý osmibitový řídicí bajt na port `#17` (desítkově 23).
* **ENTER** potvrdí, **DELETE** smaže poslední číslici a **EDIT** volbu zruší. Prázdný vstup a číslo větší než 255 nic nezmění.
* Původní kazetová funkce klávesy Y je tím nahrazena.
* při výskoku z Deavstace (SS+Q) se automaticky nastránkuje zpět stránka 64 (ZX ROM), aby nedošlo k pádu systému

## Volitelné přemístění pomocného bloku

Výchozí pomocný blok je `#5B00–#5BFF`. Cíl lze nastavit v **čerstvé, ještě nespouštěné** binárce na souborových offsetech `#0C26–#0C27` (nižší bajt první). Výchozí bajty `00 5B` znamenají `#5B00`; `00 80` znamenají `#8000`. V paměti po načtení na `#4000` jsou to adresy `#4C26–#4C27`.

Pro vytvoření samostatné kopie lze použít:

```text
python source/configure\_devastace\_relocation.py --dest 0x8000
```

Pomocný blok musí ležet ve volné zapisovatelné RAM přístupné při všech používaných stránkách. Při prvním startu se blok automaticky zkopíruje a opraví odkazy; při dalších startech stejného obrazu se už nepřemisťuje.

**Pro sledování původního obsahu `#5B00`:** před načtením uchovej jeho 256 bajtů jinde, zkopíruj *celých* 7168 bajtů Devastace na `#4000–#5BFF`, spusť první relokaci a až potom obsah `#5B00–#5BFF` vrať. Při každém dalším cyklu se vrať k čerstvé kopii binárky a konfiguruj ji znovu.

## Zdroj a kontrola

`source/Devastace\_MB03\_page\_Y.a80` obsahuje změny označené **AI1**. `source/Devastace\_MB03\_full\_rebuild.a80` skládá čitelnou upravenou část s původním obrazem (`source/MBDEVMB03\_original.bin`); ostatní původní rutiny zatím nejsou převedeny do čitelného assembleru. `source/build\_page\_patch.py` vytváří vydanou binárku bez závislosti na konkrétním assembleru.

```text
python source/build\_page\_patch.py
python source/verify\_page\_patch.py
python source/verify\_relocation.py
```

SHA-256 vydané binárky: `b5be03ca690c3dc85a3893913ddad4b717af0be7d74292d171695160c09e3003`; velikost je stejná jako u pracovní verze, **7168 bajtů**. Číselný vstup a relokace prošly modelovými kontrolami strojového kódu; uživatel na skutečném MB03+ potvrdil volbu stránky a přítomnost přemístěného kódu na `#8000`.

Rozložení: kořen `README.md`, `runable/` = program, `source/` = zdroj a nástroje, `images/` = vlastní obrázky. Původní `README\_Devastace\_MB03\_Y\_relocace\_STRUCNE\_CZ.txt` zůstává nedotčený.

