# PyLOD
PyLOD is a Python wrapper for exposing Linked Open Data from public SPARQL-served endpoints. It acts as an abstraction layer for the retrieval of structured data, such as classes, properties and individuals, without requiring any knowledge of SPARQL.

## Getting Started
PyLOD is a minimal module for Python 2.x. Support for Python 3.x will be tested and added soon.

### Prerequisites

[SPARQLWrapper](https://rdflib.github.io/sparqlwrapper/) - SPARQLWrapper is a simple Python wrapper around a SPARQL service to remotelly execute queries.

### Installation

* #### Manually
 
 1. Install [SPARQLWrapper](https://github.com/RDFLib/sparqlwrapper).
 2. Save `PyLOD.py` to your project's directory.

* #### From PyPi

  Installation from PyPi will be added soon. 

## Usage
**1. Import the PyLOD class and create a PyLOD class object.**
```python
from PyLOD import PyLOD
pylod = PyLOD()
```

**2. Provide a dictionary of desired namespaces**
```python
my_namespaces={
    "dbo": "http://dbpedia.org/ontology/",
    "dbp": "http://dbpedia.org/property/"
}

pylod.namespaces.set_namespaces(my_namespaces)
```
   This step is optional, since PyLOD already incorporates a set of known namespaces. To get the list of defined namespaces, use this:
  
  ```python
print(pylod.namespaces.get_namespaces())
```

**3. Define a dictionary of SPARQL endpoints to be queried:**
```python
my_endpoints={
    "DBpedia": "http://dbpedia.org/sparql",
    "GeoLinkedData": "http://linkedgeodata.org/sparql"
}

pylod.endpoints.set_endpoints(my_endpoints)
```
   If no endpoints are defined, PyLOD will use a pre-defined set of known endpoints. To get the list of these endpoints, do this:
  
  ```python
print(pylod.endpoints.get_endpoints())
```

**4. Use PyLOD's `expose` functions to retrieve structured data from the endpoints.**
Set the optional argument `limit_per_endpoint` to limit the results per endpoint. For example:
```python
# Get entities of type owl:Class
classes = pylod.expose.classes(limit_per_endpoint=100)

# Get the sub-classes of a specific class 
sub_classes = pylod.expose.sub_classes(super_class="dbo:Artist")

# Get instances of a specific class 
instances = pylod.expose.instances_of_class(cls="dbo:Artist", include_subclasses=True, limit_per_endpoint=50)
```

### Expose functions:
* __classes()__ - Returns class entities
* __sub_classes()__ - Returns the sub-classes of a given class 
* __super_classes()__ - Returns the super-classes of a given class 
* __equivalent_classes()__ - Returns the equivalent classes of a given class 
* __disjoint_classes()__ - Returns the disjoint classes of a given class 
* __sub_properties()__ - Returns the sub-properties of a given property 
* __super_properties()__ - Returns the super-properties of a given property 
* __triples()__ - Allows the retrieval of triples within the pattern (subject-predicate-object)
* __subjects()__ - Returns the subjects of a given predicate-object pair 
* __predicates()__ - Returns the predicates of a given subject-object pair
* __objects()__ - Returns the objects of a given subject-predicate pair
* __instances_of_class()__ - Returns instances of a given class type
* __labels()__ - Returns labels of a given entity, with an optional language argument

### SPARQL functions:
* __execute_select()__ - Allows the execution of a custom SPARQL select query to a given endpoint URL
* __execute_select_to_all_endpoints()__ - Allows the execution of a custom SPARQL select query to all endpoints defined in `pylod.endpoints.get_endpoints()`
* __is_active_endpoint()__ - Checks if a given endpoint URL is alive and responds to SPARQL queries

## Documentation
The detailed docs will be added soon.

## Authors
* [Panos Mitzias](http://pmitzias.com) - Design and development
* [Stratos Kontopoulos](http://stratoskontopoulos.com) - Contribution to the design

## Powered by
* [Centre for Research & Technology Hellas - CERTH](https://www.certh.gr/root.en.aspx)
* [Multimedia Knowledge & Social Media Analytics Laboratory - MKLab](http://mklab.iti.gr/)

## Applications
PyLOD has been deployed in the following projects:

* [PERICLES](http://project-pericles.eu/)
* [ROBORDER](http://roborder.eu/)
* [TENSOR](https://tensor-project.eu/)
* [SUITCEYES](http://suitceyes.eu/)
