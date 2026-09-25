Devastace MB03+ – Y pro Page a relokace pomocného bloku (AI1)
=============================================================

Obsah
-----
MBDEVY9.3                           Binárka 7168 bajtů, nahrát na #4000
MBDEVMB03_original.bin               Původní nezměněné tělo programu
Devastace_MB03_page_Y.a80            Zdroj pro Y, konfiguraci a relokátor
Devastace_MB03_full_rebuild.a80      Hybridní sestavitelný zdroj
build_page_patch.py                  Sestavení z původního obrazu
configure_devastace_relocation.py    Nastavení cílové adresy v nové kopii
verify_page_patch.py                 Kontrola číselného vstupu Y
verify_relocation.py                 Kontrola skutečných instrukcí relokátoru

Obsluha Y
---------
Y vytiskne Pag na dolním řádku. Původní editor Devastace #463C
vytiskne znak > a reverzní C, zadávání pokračuje na pozici #FA.
DELETE maže, EDIT ruší, ENTER potvrdí hodnotu 0..255; celý bajt
se zapíše na port #17 (desítkově 23) a do uloženého údaje
pro zobrazení aktuální stránky. Při vyšší hodnotě se nic nemění.
Soustavu čísel určuje nastavení Devastace.

Konfigurace bloku #5B00–#5BFF
-----------------------------
Dva konfigurační bajty jsou na adresách #4C26–#4C27; souborové
offsety #0C26–#0C27. Pořadí bajtů je nižší, vyšší. Výchozí
hodnota #5B00 = bajty 00 5B: program běží jako dříve.

Pro cílovou adresu například #8123 spusť:
  python3 configure_devastace_relocation.py --dest 0x8123
Vznikne soubor MBDEVY9_8123.3. Můžeš také upravit přesně dva
bajty původní MBDEVY9.3 na offsetu #0C26: hodnota #8123 je 23 81.
Nová adresa nemusí být zarovnána na #xx00. Pro cílový blok vyber
volnou, zapisovatelnou RAM přístupnou po celou dobu chodu monitoru.
Obecně použij #6000–#FF00 a dbej, aby se 256bajtový blok
nepřekrýval s testovaným programem. Spodních 16 KB se při změně
portu #17 přepíná, proto tam pomocné rutiny nedávej.

Po načtení programu na #4000 se při prvním spuštění přes #402B
spustí relokátor na #4C28. Opraví sedm externích a čtyři interní
16bitové odkazy a zkopíruje #5B00–#5BFF do konfigurované oblasti.
Nakonec vrátí původní startovací skok #402B -> #47DA, takže se při
dalším návratu do monitoru relokace znovu nespustí. Relokátor
skončí na #4C7E; zbytek do #4C8B je výplň. Soubor má stále 7168 B.

Opakované spuštění a změna konfigurace
--------------------------------------
Adresu #4C26–#4C27 změň v NEPROVEDENÉM obrazu a pak znovu nahraj
celou binárku do #4000–#5BFF. Souborový offset je #0C26–#0C27.
Pouhý restart obrazu, který už jednou běžel, nestačí: při prvním startu
se změní instrukce na #402B z C3 28 4C na C3 DA 47, takže relokátor
se přeskočí. Pro #8000 musí být v RAM #4C26–#4C27 bajty 00 80.
Po relokaci bude na #8000 počátek původní klávesnicové rutiny
2E 2F 11 FF FF 01 FE FE a volání na #45AF míří na #8000.
Nepouštěj relokátor na již přesunutém obrazu znovu: jeho odkazy
jsou upravené a původní #5B00 už může obsahovat debugovaná data.

DŮLEŽITÉ: Tato varianta sama nezachovává původní obsah #5B00.
Souvislé načtení 7168 B jej nejprve přepíše. Pokud jej chceš
později trasovat, musí jej tvé NMI menu před načtením uložit jinam,
Devastaci nahrát, nechat jednou proběhnout relokátor a teprve potom
původní obsah do #5B00 vrátit. Nepřepisuj #5B00 před dokončením
první relokace: tato rutina jej používá jako zdroj svých 256 B.

Sestavení a kontrola
-------------------
  python3 build_page_patch.py
  python3 verify_page_patch.py
  python3 verify_relocation.py
  sjasmplus --raw=MBDEVY9.3 Devastace_MB03_full_rebuild.a80

Původní SHA256:
  24c6dd199b2c7d1d30da1c07d054e319400a0cce2914e98cb78e4481c0489408
MBDEVY9.3 SHA256:
  b5be03ca690c3dc85a3893913ddad4b717af0be7d74292d171695160c09e3003

Skripty kontrolují všech 256 hodnot Page v obou soustavách a
strojový průchod relokátorem s výchozí i několika jinými adresami.
Model obrazovky není skutečný MB03+: novou konfiguraci ověř nejprve
na hardwaru s vybranou bezpečnou cílovou oblastí. Úplný původní
zdroj z binárky obnoven nebyl; ostatní program obsahuje původní bajty.
