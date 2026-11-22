## Leseliste

```dataview
table autor as "Autor", erscheinungsjahr as "Jahr", hinzugefügt as "Hinzugefügt"
from "Books/Buchliste"
where type = "book" and status = "ungelesen"
sort hinzugefügt asc
```

## Gelesen

```dataview
table autor as "Autor", dateformat(gelesen, "yyyy-MM-dd") as "Gelesen am"
from "Books/Buchliste"
where type = "book" and status = "gelesen"
sort gelesen desc
```

## Bücher pro Jahr

```dataview
table length(rows) as "Bücher"
from "Books/Buchliste"
where type = "book" and status = "gelesen"
group by dateformat(gelesen, "yyyy") as Jahr
sort Jahr desc
```

## Ohne Status (Aufräumliste)

```dataview
list
from "Books/Buchliste"
where !type or !status
```
