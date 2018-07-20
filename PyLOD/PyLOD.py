"""
PyLOD - A Python wrapper for exposing Linked Open Data from public SPARQL-served endpoints.
Version 0.1

Official webpage: http://pmitzias/PyLOD
Documentation: http://pmitzias/PyLOD/docs.html

Created by Panos Mitzias (http://www.pmitzias.com), Efstratios Kontopoulos (http://www.stratoskontopoulos.com)
Powered by CERTH/MKLab (http://mklab.iti.gr)
"""

from SPARQLWrapper import SPARQLWrapper, JSON
import re
import sys


class PyLOD:
    def __init__(self, endpoint_dictionary=None, namespaces_dictionary=None):
        """
        The PyLOD class constructor.
        :param endpoint_dictionary: Optional argument for user-defined SPARQL-served LOD endpoints given as a dictionary, where the keys are the endpoint names and the values are the endpoint URLs.
        :param namespaces_dictionary: Optional argument for user-defined namespaces given as a dictionary, where the keys are the namespace prefixes and the key values are the namespace URLs.
        """

        class Endpoints:
            def __init__(self, endpoint_dictionary=None):
                """
                The Endpoints class constructor.
                :param endpoint_dictionary: Optional argument for user-defined SPARQL-served LOD endpoints given as a dictionary, where the keys are the endpoint names and the key values are the endpoint URLs.
                """

                self.dictionary = {}
                self.set_endpoints(endpoint_dictionary)

            def set_endpoints(self, endpoint_dictionary=None):
                """
                Sets the dictionary of endpoints to be queried. If the argument endpoint_dictionary is not provided, a set of popular endpoints (e.g. DBpedia) will be used.
                :param endpoint_dictionary: A user-defined dictionary of endpoints where the keys are the endpoint names and the key values are the corresponding endpoint URLs.
                """

                if endpoint_dictionary is None:
                    # Set popular endpoints
                    self.dictionary = {
                        "DBpedia": "http://dbpedia.org/sparql",
                        "GeoLinkedData": "http://linkedgeodata.org/sparql"
                    }

                # If a user-defined endpoint dictionary was given as argument
                elif isinstance(endpoint_dictionary, dict):
                    self.dictionary = {}

                    # For each given endpoint
                    for key in endpoint_dictionary:
                        try:
                            # If given value is string
                            if isinstance(endpoint_dictionary[key], str):
                                self.dictionary[key] = endpoint_dictionary[key]
                        except Exception as e:
                            print("PyLOD.Endpoints.set_endpoints() - Error appending provided endpoint to endpoints dictionary")
                            print(e)

                else:
                    self.dictionary = {}

            def get_endpoints(self):
                """
                :return: The dictionary of currently set endpoints.
                """

                return self.dictionary

        class Namespaces:
            def __init__(self, namespace_dictionary):
                """
                The Namespaces class constructor.
                :param namespace_dictionary: Optional argument for a user-defined dictionary of namespaces where the keys are the desired prefixes and the key values are the corresponding namespace URLs.
                """
                self.dictionary = self.set_namespaces(namespace_dictionary)

            def set_namespaces(self, namespace_dictionary=None):
                """
                Returns a dictionary of the most popular namespaces (rdf, rdfs, etc.). The argument namespace_dictionary may contain a dictionary of user-defined namespaces.
                :param namespace_dictionary: A user-defined dictionary of namespaces where the keys are the desired prefixes and the key values are the corresponding namespace URLs
                :return: A dictionary of namespaces.
                """

                # Popular namespaces
                namespaces = {
                    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                    "prov": "http://www.w3.org/ns/prov#",
                    "foaf": "http://xmlns.com/foaf/0.1/",
                    "xml": "http://www.w3.org/2001/XMLSchema#",
                    "owl": "http://www.w3.org/2002/07/owl#",
                    "db": "http://dbpedia.org/",
                    "dbo": "http://dbpedia.org/ontology/",
                    "dbp": "http://dbpedia.org/property/"
                }

                # If a user-defined namespace dictionary was given as argument
                if (namespace_dictionary is not None) and (isinstance(namespace_dictionary, dict)):

                    # For each given namespace prefix
                    for prefix in namespace_dictionary:

                        try:
                            namespaces[prefix] = namespace_dictionary[prefix]
                        except Exception as e:
                            print("PyLOD.Namespaces.set_namespaces() - Error appending provided namespace to namespace dictionary")
                            print(e)

                return namespaces

            def get_namespaces(self):
                """
                :return: The dictionary of currently set namespaces.
                """
                return self.dictionary

            def get_namespaces_string(self):
                """
                Concatenates all namespaces in the namespace dictionary into a string, in order to be used in SPARQL queries
                :return: A string that complies with W3C SPARQL definition of namespaces
                """

                namespaces_string = ''

                for prefix in self.dictionary:
                    try:
                        namespaces_string += "PREFIX %s: <%s>\n" % (prefix, self.dictionary[prefix])
                    except Exception as e:
                        print("PyLOD.Namespaces.get_namespaces_string() - Error while generating namespaces string from namespace dictionary")
                        print(e)

                return namespaces_string

        class SPARQL:
            def __init__(self, pylod):
                """
                The SPARQL class constructor.
                :param pylod: SPARQL's parent class object (PyLOD object).
                """

                self.pylod = pylod

            def execute_select(self, endpoint_url, query, limit=None):
                """
                Uses the SPARQLWrapper module to execute a SPARQL query against the given endpoint.
                :param endpoint_url: A URL of the SPARQL-served endpoint to be queried.
                :param query: The desired SPARQL query.
                :param limit: Optional argument (integer) to limit query results.
                :return: The query results as a dictionary (JSON format).
                """

                if (not self.pylod.is_valid_string(endpoint_url)) and (not self.pylod.is_valid_string(query)):
                    print("PyLOD.SPARQL.execute_select() - Invalid arguments")
                    return False

                # Connect to ontology
                sparql = SPARQLWrapper(endpoint_url)

                # Add prefixes to query
                query = self.pylod.namespaces.get_namespaces_string() + query

                # Add limit to query
                if (limit is not None) and (isinstance(limit, int)):
                    query = query + ' LIMIT ' + str(limit)

                # Set query
                try:
                    sparql.setQuery(query)
                # In case it is not unicode
                except TypeError:
                    sparql.setQuery(unicode(query))

                # Set output to JSON
                sparql.setReturnFormat(JSON)

                try:
                    # Execute query and return results
                    return sparql.query().convert()['results']['bindings']
                except Exception as e:
                    # print("PyLOD.SPARQL.execute_select() - Error while executing query to ", endpoint_url)
                    # print(e)
                    return False

            def execute_select_to_all_endpoints(self, query, limit_per_endpoint=None):
                """
                Executes the given query against all endpoints in the endpoint dictionary.
                :param query: The desired SPARQL query.
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: A dictionary with the query results per endpoint.
                """

                if not self.pylod.is_valid_string(query) or (limit_per_endpoint is not None and not isinstance(limit_per_endpoint, int)):
                    print("PyLOD.SPARQL.execute_select_to_all_endpoints() - Invalid arguments")
                    return False

                results = {}

                # Get the endpoints dictionary
                endpoints = self.pylod.endpoints.get_endpoints()

                # For each endpoint
                for endpoint_name in endpoints:

                    sys.stdout.write("Querying \033[95m" + str(endpoint_name) + "\033[0m | Endpoint status:")

                    # If endpoint is reachable
                    if self.pylod.sparql.is_active_endpoint(endpoint_url=endpoints[endpoint_name]):

                        sys.stdout.write("\033[92m ACTIVE \033[0m")

                        try:
                            results[endpoint_name] = self.pylod.sparql.execute_select(
                                endpoint_url=endpoints[endpoint_name],
                                query=query,
                                limit=limit_per_endpoint)

                            if results[endpoint_name]:
                                sys.stdout.write("| Results:\033[92m RETRIEVED \033[0m \n")
                            else:
                                sys.stdout.write("| Results:\033[91m NOT RETRIEVED \033[0m \n")

                        except Exception as e:
                            print("PyLOD.SPARQL.execute_select_to_all_endpoints() - Error while executing query to ", endpoint_name)
                            print(e)
                    else:
                        sys.stdout.write("\033[91m UNREACHABLE \033[0m")
                        sys.stdout.write("| Results: \033[91m NOT RETRIEVED \033[0m \n")

                        results[endpoint_name] = None

                    sys.stdout.flush()

                return results

            def is_active_endpoint(self, endpoint_url):
                """
                Checks if the given endpoint URL corresponds to an active SPARQL-served endpoint.
                :param endpoint_url: The endpoint URL to check.
                :return: True if endpoint is active, False if endpoint is not reachable.
                """

                # Try to make a selection
                if not self.execute_select(endpoint_url, 'SELECT ?x WHERE {?x ?y ?z}', limit=1):
                    return False
                else:
                    return True

        class Expose:
            def __init__(self, pylod):
                """
                The Expose class constructor.
                :param pylod: Expose's parent class object (PyLOD object).
                """

                self.pylod = pylod

            def classes(self, limit_per_endpoint=None):
                """
                Exposes URIs of classes.
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT (?class AS ?uri)
                            WHERE {
                                ?class rdf:type owl:Class .
                            }
                          """,
                    limit_per_endpoint=limit_per_endpoint)

            def sub_classes(self, super_class, limit_per_endpoint=None):
                """
                Exposes URIs of entities that are sub classes of the given class.
                :param super_class: The desired class to expose its sub classes.
                Should be given either with a known prefix (e.g. "dbo:Artist") or with the complete URI (e.g. "http://dbpedia.org/ontology/Artist").
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """

                # Validate given argument
                if self.pylod.is_valid_string(super_class):
                    if self.pylod.is_url(super_class):
                        super_class = "<" + super_class + ">"

                else:
                    print("PyLOD.Expose.sub_classes() - Invalid argument")
                    return False

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT (?subclass AS ?uri)
                            WHERE {
                                ?subclass rdfs:subClassOf %s .
                            }
                          """ % (super_class,),
                    limit_per_endpoint=limit_per_endpoint)

            def super_classes(self, sub_class, limit_per_endpoint=None):
                """
                Exposes URIs of entities that are super classes of the given class.
                :param sub_class: The desired class to expose its super classes.
                Should be given either with a known prefix (e.g. "dbo:Artist") or with the complete URI (e.g. "http://dbpedia.org/ontology/Artist").
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """
                # Validate given argument
                if self.pylod.is_valid_string(sub_class):
                    if self.pylod.is_url(sub_class):
                        sub_class = "<" + sub_class + ">"

                else:
                    print("PyLOD.Expose.super_classes() - Invalid argument")
                    return False

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT (?superclass AS ?uri)
                            WHERE {
                                 %s rdfs:subClassOf ?superclass .
                            }
                          """ % (sub_class,),
                    limit_per_endpoint=limit_per_endpoint)

            def equivalent_classes(self, cls, limit_per_endpoint=None):
                """
                Exposes URIs of entities that are equivalent classes of the given class.
                :param cls: The desired class to expose its equivalent classes.
                Should be given either with a known prefix (e.g. "dbo:Artist") or with the complete URI (e.g. "http://dbpedia.org/ontology/Artist").
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """

                # Validate given argument
                if self.pylod.is_valid_string(cls):
                    if self.pylod.is_url(cls):
                        cls = "<" + cls + ">"
                else:
                    print("PyLOD.Expose.equivalent_classes() - Invalid argument")
                    return False

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT (?equivalent_class AS ?uri)
                            WHERE {
                                 ?equivalent_class owl:equivalentClass %s .
                            }
                          """ % (cls,),
                    limit_per_endpoint=limit_per_endpoint)

            def disjoint_classes(self, cls, limit_per_endpoint=None):
                """
                Exposes URIs of entities that are disjoint classes of the given class.
                :param cls: The desired class to expose its disjoint classes.
                Should be given either with a known prefix (e.g. "dbo:Artist") or with the complete URI (e.g. "http://dbpedia.org/ontology/Artist").
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """

                # Validate given argument
                if self.pylod.is_valid_string(cls):
                    if self.pylod.is_url(cls):
                        cls = "<" + cls + ">"
                else:
                    print("PyLOD.Expose.disjoint_classes() - Invalid argument")
                    return False

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT (?disjoint_class AS ?uri)
                            WHERE {
                                 ?disjoint_class owl:disjointWith %s .
                            }
                          """ % (cls,),
                    limit_per_endpoint=limit_per_endpoint)

            def sub_properties(self, super_property, limit_per_endpoint=None):
                """
                Exposes URIs of properties that are sub properties of the given property.
                :param super_property: The desired property to expose its sub properties.
                Should be given either with a known prefix (e.g. "rdfs:label") or with the complete URI (e.g. "https://www.w3.org/2000/01/rdf-schema#label").
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """

                # Validate given argument
                if self.pylod.is_valid_string(super_property):
                    if self.pylod.is_url(super_property):
                        super_property = "<" + super_property + ">"

                else:
                    print("PyLOD.Expose.sub_properties() - Invalid argument")
                    return False

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT (?subproperty AS ?uri)
                            WHERE {
                                ?subproperty rdfs:subPropertyOf %s .
                            }
                          """ % (super_property,),
                    limit_per_endpoint=limit_per_endpoint)

            def super_properties(self, sub_property, limit_per_endpoint=None):
                """
                Exposes URIs of properties that are super properties of the given property.
                :param sub_property: The desired property to expose its super properties.
                Should be given either with a known prefix (e.g. "rdfs:label") or with the complete URI (e.g. "https://www.w3.org/2000/01/rdf-schema#label").
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """

                # Validate given argument
                if self.pylod.is_valid_string(sub_property):
                    if self.pylod.is_url(sub_property):
                        sub_property = "<" + sub_property + ">"

                else:
                    print("PyLOD.Expose.super_properties() - Invalid argument")
                    return False

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT (?superproperty AS ?uri)
                            WHERE {
                                %s rdfs:subPropertyOf ?superproperty .
                            }
                          """ % (sub_property,),
                    limit_per_endpoint=limit_per_endpoint)

            def subjects(self, predicate, object, limit_per_endpoint=None):
                """
                Exposes entities found as subjects with the given predicate and object, within the scope of the tiple pattern Subject-Predicate-Object.
                :param predicate: The desired predicate (either as a full URI or with a known namespace)
                :param object: The desired object (either as a full URI or with a known namespace)
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """

                # Validate given arguments
                if self.pylod.is_valid_string(predicate) and self.pylod.is_valid_string(object):
                    if self.pylod.is_url(predicate):
                        predicate = "<" + predicate + ">"
                    if self.pylod.is_url(object):
                        object = "<" + object + ">"

                else:
                    print("PyLOD.Expose.subjects() - Invalid arguments")
                    return False

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT (?subject AS ?uri)
                            WHERE {
                                ?subject %s %s .
                            }
                          """ % (predicate, object),
                    limit_per_endpoint=limit_per_endpoint)

            def predicates(self, subject, object, limit_per_endpoint=None):
                """
                Exposes entities found as predicates with the given subject and object, within the scope of the tiple pattern Subject-Predicate-Object.
                :param subject: The desired subject (either as a full URI or with a known namespace)
                :param object: The desired object (either as a full URI or with a known namespace)
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """

                # Validate given arguments
                if self.pylod.is_valid_string(subject) and self.pylod.is_valid_string(object):
                    if self.pylod.is_url(subject):
                        subject = "<" + subject + ">"
                    if self.pylod.is_url(object):
                        object = "<" + object + ">"

                else:
                    print("PyLOD.Expose.predicates() - Invalid arguments")
                    return False

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT (?predicate AS ?uri)
                            WHERE {
                                %s ?predicate %s .
                            }
                          """ % (subject, object),
                    limit_per_endpoint=limit_per_endpoint)

            def objects(self, subject, predicate, limit_per_endpoint=None):
                """
                Exposes entities found as objects with the given subject and predicate, within the scope of the tiple pattern Subject-Predicate-Object.
                :param subject: The desired subject (either as a full URI or with a known namespace)
                :param predicate: The desired predicate (either as a full URI or with a known namespace)
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """

                # Validate given arguments
                if self.pylod.is_valid_string(subject) and self.pylod.is_valid_string(predicate):
                    if self.pylod.is_url(subject):
                        subject = "<" + subject + ">"
                    if self.pylod.is_url(predicate):
                        predicate = "<" + predicate + ">"

                else:
                    print("PyLOD.Expose.objects() - Invalid arguments")
                    return False

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT (?object AS ?uri)
                            WHERE {
                                %s %s ?object .
                            }
                          """ % (subject, predicate),
                    limit_per_endpoint=limit_per_endpoint)

            def triples(self, subject=None, predicate=None, object=None, limit_per_endpoint=None):
                """
                Exposes triples with the given subject and/or predicate and/or object, within the scope of the tiple pattern Subject-Predicate-Object.
                If any of the arguments (subject, predicate, object) is not defined (None), then it will act as a variable in the query.
                :param subject: Optional argument. If not provided, triples will be returned where the subject is variable.
                :param predicate: Optional argument. If not provided, triples will be returned where the predicate is variable.
                :param object: Optional argument. If not provided, triples will be returned where the object is variable.
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """
                
                # Validate arguments and initialize not given arguments

                # Subject argument
                if subject is None:
                    subject = "?subject"
                elif self.pylod.is_valid_string(subject):
                    if self.pylod.is_url(subject):
                        subject = "<" + subject + ">"
                else:
                    print("PyLOD.Expose.triples() - Invalid subject argument")
                    return False

                # Predicate argument
                if predicate is None:
                    predicate = "?predicate"
                elif self.pylod.is_valid_string(predicate):
                    if self.pylod.is_url(predicate):
                        predicate = "<" + predicate + ">"
                else:
                    print("PyLOD.Expose.triples() - Invalid predicate argument")
                    return False

                # Object argument
                if object is None:
                    object = "?object"
                elif self.pylod.is_valid_string(object):
                    if self.pylod.is_url(object):
                        object = "<" + object + ">"
                else:
                    print("PyLOD.Expose.triples() - Invalid object argument")
                    return False

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT ?subject ?predicate ?object
                            WHERE {
                                %s %s %s .
                            }
                          """ % (subject, predicate, object),
                    limit_per_endpoint=limit_per_endpoint)

            def instances_of_class(self, cls, include_subclasses=False, limit_per_endpoint=None):
                """
                Exposes instances of the given class and (optionally) its subclasses.
                :param cls: The desired class to be queried for isntances.
                :param include_subclasses: Optional argument (boolean). If True, instances from cls's subclasses will also be returned.
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """

                # Validate given argument
                if self.pylod.is_valid_string(cls):
                    if self.pylod.is_url(cls):
                        cls = "<" + cls + ">"

                else:
                    print("PyLOD.Expose.instances_of_class() - Invalid argument")
                    return False

                # Check if subclasses of cls should be included
                predicate = "rdf:type"
                if include_subclasses:
                    predicate += "*"

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT (?instance AS ?uri)
                            WHERE {
                                 ?instance %s %s .
                            }
                          """ % (predicate, cls,),
                    limit_per_endpoint=limit_per_endpoint)

            def labels(self, entity, language=None, limit_per_endpoint=None):
                """
                Exposes the labels of entities. Optionally, a language tag can be defined.
                :param entity: The URI of entity to retrieve its labels
                :param language: Optional language parameter as defined in BCP 47.
                :param limit_per_endpoint: Optional argument (integer) to limit query results per endpoint.
                :return: The query results as a dictionary (JSON format).
                """

                # Validate given argument
                if self.pylod.is_valid_string(entity):
                    if self.pylod.is_url(entity):
                        entity = "<" + entity + ">"

                else:
                    print("PyLOD.Expose.labels() - Invalid argument")
                    return False

                language_filter = ""

                # Check if a language tag is selected
                if language is not None and self.pylod.is_valid_string(language):
                    language_filter = "FILTER (LANG(?label) = '%s')" % (language,)

                # Execute query
                return self.pylod.sparql.execute_select_to_all_endpoints(
                    query="""
                            SELECT DISTINCT ?label
                            WHERE {
                                 %s rdfs:label ?label .
                                 %s
                            }
                          """ % (entity, language_filter,),
                    limit_per_endpoint=limit_per_endpoint)

        self.endpoints = Endpoints(endpoint_dictionary=endpoint_dictionary)
        self.namespaces = Namespaces(namespace_dictionary=namespaces_dictionary)
        self.sparql = SPARQL(pylod=self)
        self.expose = Expose(pylod=self)

    def is_url(self, text):
        """
        Checks if a given string is a URL.
        :param text: The string to be tested.
        :return: True if URL, False if not a URL.
        """

        regex = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        try:
            return re.match(regex, text) is not None
        except Exception as e:
            print("PyLOD.is_url() - Invalid argument")
            print(e)
            return False

    def is_valid_string(self, arg):
        """
        Checks if the given argument is a non-empty, non-whitespace string
        :param arg: The argument to check.
        :return: True if valid string, False if not
        """

        if isinstance(arg, str) and arg and (not arg.isspace()):
            return True

        return False

if __name__ == '__main__':
    print("Please visit http://pmitzias/PyLOD/docs.html for usage instructions.")



