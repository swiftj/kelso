# Welcome to Project Kelso

Kelso is a simple RESTful web service that I wrote that does a couple things. Generally speaking, when this service 
receives data from a client, it processes or 'cleans' the data by removing duplicate entries and invalid categories 
(more on categories in a moment). The order of the entries in the input is preserved, with the duplicates and 
invalid categories removed. Additionally, the output also includes the total count of each valid category encountered
by this web service and in the resulting output. Incidentally, the list of valid categories is predefined when the
service starts and is as follows:

* PERSON
* PLACE
* ANIMAL
* COMPUTER
* OTHER

## Data Cleaning

The data that this web service expects is a list of category-subcategory name value pairs encoded in JSON. The list may 
contain duplicate category names provided their corresponding subcategories values are unique. For example, the 
following two categories are acceptable and are fully preserved as part of the cleaning process:

```
{ categories : ['PERSON', 'John'], ['PERSON', 'Steve'] }
```

However if both subcategory values are identical, this service will remove such duplicate pairs to ensure there is 
only one unique category-subcategory pair per cleaned output document. For example, assuming the following contrived
input data:

```
{ categories : ['PERSON', 'John'], ['PERSON', 'John'] }
```

Is effectively equivalent to the following:

```
{ categories : ['PERSON', 'John'] }
```
 
In short, only unique name-value pairs are preserved as part of the cleaned output. Similarly, as mentioned earlier,
any category-subcategory pair that does not have a matching category name from the master list of categories will 
result in the entire pair being ignored / removed by this service. For example, consider the following input:

```
{"categories": [["PERSON", "John"], ["ANIMAL", "Dog"], ["FOO", "Bar"], ["ANIMAL", "Bird"]]}
```

This web service will produce the following resulting output:

```
{"categories": [["PERSON", "John"], ["ANIMAL", "Dog"], ["ANIMAL", "Bird"]], "counts": {"PERSON": 1, "ANIMAL": 3}}
```

Notice that this service tallies the total number of valid categories-subcategory pairs that it finds in the input 
data includes those counts in the output.

## Category Management

In addition to processing and cleaning input data, the kelso web service also provides the ability to add and delete 
categories from this master list. Additionally, this service will display the running total of counts for every 
category in this list. These counts are tallied across every client submission so they are aggregate values for all
submissions. The master list looks like the following at service startup:

```
{
  "COMPUTER": 0,
  "PERSON": 0,
  "PLACE": 0,
  "OTHER": 0,
  "ANIMAL": 0
}
```

## Deployment and Testing

This service is written completely in [Python](https://www.python.org/) and utilizes the [Flask](http://flask.pocoo.org/)
microframework. You can pull the code to your local workspace and run a local instance of the service from the command
line.

```
 $ python service.py
  * Running on https://0.0.0.0:5000/ (Press CTRL+C to quit)
  * Restarting with stat
``` 

At this point, you may use your favorite REST client to start using the service located at the URL displayed at startup.