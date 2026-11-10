# Hard-case categories and judging rules

Target: 10 sentences per category in `data/hard_cases.csv`. The rows there
now are machine-written seeds; a native speaker must check and extend them.

| Category | What goes in `text` | Example of the trap |
|---|---|---|
| `phone` | 10-digit mobile and landline numbers | read as one huge number instead of digits |
| `currency` | ₹ amounts, lakhs and crores, paise | symbol skipped; Western grouping instead of lakh/crore |
| `date` | numeric and written dates, years | year read digit by digit |
| `time` | clock times, durations | "6:45" read as two unrelated numbers |
| `cardinal` | plain quantities with Indian comma grouping | 1,25,000 misread |
| `percent` | percentages and decimals | decimal point dropped |
| `measure` | units: కి.మీ., కేజీ, °C, km/h | abbreviation spelled out letter by letter |
| `math` | simple expressions with + - × ÷ = | operators skipped |
| `email` | email addresses and URLs | symbols skipped; domain garbled |
| `alphanumeric` | vehicle numbers, PNR, PIN codes, flight numbers | letters and digits merged |
| `codemix` | English words in Latin script inside Telugu sentences | English word dropped or read with wrong sounds |
| `control` | ordinary Telugu, no digits or English | should be near-perfect; checks the listener and the voice |

## Columns

- `text`: exactly what the TTS receives, as a person would type it.
- `spoken`: ONE acceptable spoken form, fully written out in Telugu script.
  Used only for the automatic (ASR) score. Leave empty when it equals `text`.

## Judging a clip (listening page)

Mark **correct** when every piece of information is spoken, with the right
value, in a form a Telugu speaker would accept. More than one reading can be
correct: "ప్లస్" and "కూడితే" are both fine for "+". Voice quality, accent
and speed do not matter here.

Mark **wrong** and pick the first type that applies:

| Type | Meaning |
|---|---|
| skipped | part of the content is not spoken at all |
| wrong value | a different number, date or word is spoken |
| wrong language | the item is read in English or Hindi where Telugu is expected |
| wrong reading style | values right but form unacceptable (phone number as a quantity) |
| garbled | unintelligible at that point |
| other | anything else; describe it in the note |

Mark **unsure** if you cannot decide after two plays. Do not guess.
