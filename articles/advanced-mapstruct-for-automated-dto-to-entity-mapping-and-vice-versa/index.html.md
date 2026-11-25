---
title: "Advanced MapStruct: map DTOs and entities with @Mapping"
description: "Advanced MapStruct: map fields between different DTO and Entity objects explicitly with @Mapping, from pom.xml setup to a working Spring controller."
canonical: https://ngvoicu.dev/articles/advanced-mapstruct-for-automated-dto-to-entity-mapping-and-vice-versa/
author: Gabriel Voicu
published: 2019-10-09
---

# Advanced MapStruct for automated DTO to Entity mapping and vice versa

By Gabriel Voicu, 9 October 2019

Originally published on the ZeeSpire blog.

Start this tutorial about MapStruct with [the introduction](https://ngvoicu.dev/articles/mapstruct-for-automated-dto-to-entity-mapping-and-vice-versa/).

MapStruct tries to map the field from one object to another automatically but when the objects are different you can map the object's fields explicitly.

pom.xml

```
<dependencies>
<dependency>
        <groupId>org.mapstruct</groupId>
        <artifactId>mapstruct-jdk8</artifactId>
        <version>1.2.0.Final</version>
    </dependency>
</dependencies>
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.5.1</version>
            <configuration>
                <source>1.8</source>
                <target>1.8</target>
                <annotationProcessorPaths>
                    <path>
                        <groupId>org.mapstruct</groupId>
                        <artifactId>mapstruct-processor</artifactId>
                        <version>1.2.0.Final</version>
                    </path>
                </annotationProcessorPaths>
            </configuration>
        </plugin>
    </plugins>
</build>
```

Animal class

```
public class Animal {
    private Breed breed;
    private Owner owner;
    //getters & setters
}
```

Breed class

```
public class Breed {
    private String name;
    private String country;
    private Integer height;
    //getters & setters
}
```

Owner class

```
public class Owner {
    private String name;
    private String address;
    //getters & setters
}
```

AnimalDTO class

```
public class AnimalDTO {
    private String xName;
    private String zName;
    //getters & setters
}
```

## The Mapper

AnimalAnimalDTOMapper Interface

```
@Mapper
public interface AnimalAnimalDTOMapper {
    AnimalAnimalDTOMapper INSTANCE = Mappers.getMapper(AnimalAnimalDTOMapper.class);

    @Mappings({
            @Mapping(source = "breed.name", target = "xName"),
            @Mapping(source = "owner.name", target = "zName")}
    )
    AnimalDTO objToDto(Animal animal);

    Animal dtoToObj(AnimalDTO animalDTO);
}
```

## And the action begins

```
@GetMapping(value = "/mapstruct_adv_obj_to_dto.action")
public AnimalDTO mapstructAdvObjToDto() {
    Animal animal = new Animal(
            new Breed("Boxer", "Germany", 120),
            new Owner("Gabriel Voicu", "Krakovia 10A")
    );
    AnimalDTO animalDTO = AnimalAnimalDTOMapper.INSTANCE.objToDto(animal);
    return animalDTO;
}
```

Gabriel Voicu

I’m a software engineer. I build AI agents that work inside large systems, and I write open-source tools for coding agents.

[More about me](https://ngvoicu.dev/about/)
