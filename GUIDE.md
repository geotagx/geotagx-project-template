### Binary input
```
type:binary
```

### Dropdown lists
```
type:dropdown-list
parameters:{
	options:array,
	prompt:string,
	size:number
}
```

### Single-choice input
```
type:select
parameters:{
	options:array
}
```

### Check lists
```
type:checklist
parameters:{
	options:array,
	size:number
}
```

### Illustrative check lists
```
type:illustrative-checklist
parameters:{
	options:array,
	size:number
}
```

### Short text input
```
type:text
parameters:{
	placeholder:string,
	maxlength:number
}
```

### Long text input
```
type:longtext
parameters:{
	placeholder:string,
	maxlength:number
}
```

### Number input
```
type:number
parameters:{
	placeholder:string,
	min:number,
	max:number
}
```

### Date and time input
```
type:datetime
parameters:{
	mindate:string,
	maxdate:string,
	mintime:string,
	maxtime:string
}
```

### Date input
```
type:date
parameters:{
	min:string,
	max:string
}
```

### URL input
```
type:url
parameters:{
	placeholder:string
}
```

### Geotagging input
```
type:geotagging
parameters:{
	location:string
}
```
