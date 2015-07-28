### Binary input
```
type:binary
answer:{
	key:string
}
```

### Dropdown lists
```
type:dropdown-list
answer:{
	key:string,
	choices:array,
	prompt:string,
	size:integer
}
```

### Single-choice input
```
type:select
answer:{
	key:string,
	choices:array
}
```

### Check lists
```
type:checklist
answer:{
	key:string,
	choices:array,
	size:integer
}
```

### Illustrative check lists
```
type:illustrative-checklist
answer:{
	key:string,
	choices:array,
	size:integer
}
```

### Short text input
```
type:text
answer:{
	key:string,
	placeholder:string,
	maxlength:integer
}
```

### Long text input
```
type:longtext
answer:{
	key:string,
	placeholder:string,
	maxlength:integer
}
```

### Number input
```
type:number
answer:{
	key:string,
	placeholder:string,
	min:integer,
	max:integer
}
```

### Date and time input
```
type:datetime
answer:{
	key:string,
	mindate:string,
	maxdate:string,
	mintime:string,
	maxtime:string
}
```

### Date input
```
type:date
answer:{
	key:string,
	min:string,
	max:string
}
```

### URL input
```
type:url
answer:{
	key:string,
	placeholder:string
}
```

### Geotagging input
```
type:geotagging
answer:{
	key:string
}
```
