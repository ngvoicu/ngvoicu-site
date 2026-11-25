---
title: "MapStruct: automated DTO to entity mapping in Spring"
description: "A Spring code example showing how to use MapStruct to convert entities into DTOs and back, from Maven setup to a Mapper interface and controller."
canonical: https://ngvoicu.dev/articles/mapstruct-for-automated-dto-to-entity-mapping-and-vice-versa/
author: Gabriel Voicu
published: 2019-10-08
---

# MapStruct for automated DTO to Entity mapping and vice-versa

By Gabriel Voicu, 8 October 2019

Originally published on the ZeeSpire blog.

This code example demonstrates the use of MapStruct when we need to convert basic objects into DTOs.

We start by adding the MapStruct dependencies to a Spring project. Here we use a new project but the procedure is the same for mature projects as well.

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

For each entity we need a Mapper interface:

UtilizatorUtilizatorDTOMapper Interface

```
@Mapper
public interface UtilizatorUtilizatorDTOMapper {
    UtilizatorUtilizatorDTOMapper INSTANCE = Mappers.getMapper(UtilizatorUtilizatorDTOMapper.class);
    UtilizatorDTO objToDto(Utilizator utilizator);
    Utilizator dtoToObj(UtilizatorDTO destination);
}
```

Now we can build the entity and DTO:

Utilizator Entity

```
public class Utilizator {
    private String name;
    private String address;
    public Utilizator() {
    }
    public Utilizator(String name, String address) {
        this.name = name;
        this.address = address;
    }
    //getters & setters
}
```

UtilizatorDTO

```
public class UtilizatorDTO {
    private String name;
    public UtilizatorDTO() {
    }
    public UtilizatorDTO(String name) {
        this.name = name;
    }
    //getters & setters
}
```

For demonstration purpose we are going to use a Controller class to test our Mapper.

Controller class

```
@RestController
class Controller {
    @GetMapping(value = "/mapstruct_simple_obj_to_dto.action")
    public UtilizatorDTO mapstructSimpleObjToDto() {
        Utilizator utilizator = new Utilizator("Gabi", "Krakovia 9A");
        UtilizatorDTO utilizatorDTO = UtilizatorUtilizatorDTOMapper.INSTANCE.objToDto(utilizator);
        return utilizatorDTO;
    }

    @GetMapping(value = "/mapstruct_simple_dto_to_obj.action")
    public Utilizator mapstructSimpleDtoToObj() {
        UtilizatorDTO utilizatorDTO = new UtilizatorDTO("Gabi");
        Utilizator utilizator = UtilizatorUtilizatorDTOMapper.INSTANCE.dtoToObj(utilizatorDTO);
        return utilizator;
    }
}
```

Gabriel Voicu

I’m a software engineer. I build AI agents that work inside large systems, and I write open-source tools for coding agents.

[More about me](https://ngvoicu.dev/about/)
