# stat.gibdd.ru парсер

Package that presents an API to retrieve data about the automobile crashes in the RU region 
[source of data (RF)](https://stat.gibdd.ru).

# 
## CLI

Package contains a CLI application which provides an easy interface to the package API. 
Next are a few examples of using the CLI, you can find a comprehensive documentation with the command `gibdd --help`

An example of getting information in the Excel format for a region with code 90401 for a single month in 2019.
```
gibdd verbose -ds 2019-01 -de 2019-02 -R 90 -r 90401
```


## DEV



### Build
Use `poetry install` to build a package to use
