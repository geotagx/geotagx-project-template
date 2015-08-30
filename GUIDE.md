# Using the template builder

To build your project using this template, we have added a few more requirements
that you will need to specify in your project configuration. We have also added
the possibility of defining a tutorial configuration that allows you to create
one or more tutorials to complement your project.

Both of the aforementioned configurations can be written in either **JSON** or
**YAML** formats although to keep things simple, the examples in this guide
use the JSON format.


## 1. The project configuration (project.json/project.yaml)

The project configuration -- based on the classic PyBossa configuration -- has been
extended to include a few requirements to help create a project's task presenter.
In addition to the `name`, `short_name` and `description` fields required in all PyBossa projects, you will need to specify the following fields:
- `why`: a reminder to volunteers about the importance of their contribution to the project.
- `questionnaire`: a list of at least one or more questions asked to volunteers.


### 1.a Questionnaires

The `questionnaire` is a list of entries where each is comprised of
- a unique **key** to identify each question
- the **type** of question to ask
- the **question** to ask
- a short **hint** about the question
- a set of **parameters** that configure the entry's behavior
- a **branch** field to determine the questionnaire's control flow

Please note that the `key`, `type` and `question` fields are mandatory, while the rest are optional.

#### 1.a.i Keys

#### 1.a.ii Help

#### 1.a.iii Types and parameters

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

#### 1.a.iv Control flow



## 2. The tutorial configuration (tutorial.json/tutorial.yaml)

Project tutorials are a great way of introducing volunteers to your project and
while optional, it is highly recommended that you include one in your project.

The tutorial configuration is comprised of one or more tutorials where each one
contains the following fields:
- `image`: a direct link to an image to analyse.
- `image_source`: a link to a web page that provides contextual information about `image`.
- `assertions`: a set of assertions about `image`.
