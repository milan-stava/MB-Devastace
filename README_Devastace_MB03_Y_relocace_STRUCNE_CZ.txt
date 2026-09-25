Devastace MB03+ — volba stránky Y a relokace #5B00
===================================================

Binárka: MBDEVY9.3, délka 7168 bajtů, start na #4000.

Použití Y
---------
Stiskni Y. Na spodním řádku se zobrazí „Pag“, za znakem > piš číslo.
Reverzní C označuje místo pro další znak. Číselnou soustavu určuje
aktuální nastavení Devastace: desetinně 0–255, hexadecimálně 00–FF.
Zadává se celý osmibitový řídicí bajt portu #17, včetně vyšších bitů.
ENTER potvrdí, DELETE smaže poslední číslici, EDIT volbu zruší.
Prázdný vstup nebo číslo nad 255 stránku nezmění.

Nastavení umístění pomocných rutin
----------------------------------
Výchozí umístění 256bajtového bloku je #5B00. Novou adresu nastav
v ČERSTVÉ kopii binárky, ještě před jejím prvním spuštěním:

  souborové offsety: #0C26–#0C27 (nižší bajt, vyšší bajt)
  adresy po načtení na #4000: #4C26–#4C27
  výchozí hodnota #5B00: 00 5B
  příklad pro #8000: 00 80

Při ukládání kopie pod #4000 použij offset #0C26 vzhledem k jejímu
začátku. Zvolených 256 bajtů musí být volná, zapisovatelná RAM
dostupná i při přepínání portu #17; například #8000, pokud ji
nepoužívá sledovaný program.

Opakované spuštění z NMI menu se zachováním původního #5B00
---------------------------------------------------------
Při KAŽDÉM cyklu vyjdi z čerstvé, dosud nespouštěné kopie MBDEVY9.3:

1. V této kopii nastav dva konfigurační bajty.
2. Ulož původní obsah #5B00–#5BFF mimo tuto oblast.
3. Zkopíruj CELÝCH 7168 bajtů Devastace na #4000–#5BFF.
4. Spusť Devastaci od #4000. Při tomto prvním startu sama přesune
   svůj pomocný blok z #5B00 na zvolenou adresu a opraví odkazy.
5. Po dokončení prvního přesunu vrať uložený obsah do #5B00–#5BFF.

Nepřepisuj #5B00 mezi body 3 a 4: relokátor z něj potřebuje přečíst
svých 256 bajtů. Samotné uložení binárky pod #4000 původní #5B00
nezachrání — při bodu 3 se přepíše. V už spuštěné Devastaci změna
konfiguračních bajtů další přesun nevyvolá; použij opět čerstvou kopii.
