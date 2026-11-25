---
title: "Code coverage: what it is and how to measure it"
description: "Code coverage is a metric showing the percentage of production code covered by tests, helping you spot untested lines with IDEs or SonarQube."
canonical: https://ngvoicu.dev/articles/what-is-and-how-do-we-measure-code-coverage/
author: Gabriel Voicu
published: 2019-10-26
---

# What is and how do we measure code coverage

By Gabriel Voicu, 26 October 2019

Originally published on the ZeeSpire blog.

Test quality is very important and one of the most important things in building quality tests is to cover all production code lines with tests.

Code coverage is a metric that shows us the percentage of code that is covered by tests. Using test coverage we can also identify the lines of code that we missed.

![IntelliJ coverage table by package: class, method and line coverage, with the model package at 61% of methods and 56% of lines](https://ngvoicu.dev/articles/what-is-and-how-do-we-measure-code-coverage/images/coverage1.png)

Using IntelliJ Idea to check for code coverage.

All modern IDEs have a tool that allows us to run tests with code coverage. This way we will be able to see what methods and lines of production code we didn’t cover and write more tests before pushing the code into a repository. Another great way to check code coverage is to use a tool like SonarQube.

![IntelliJ editor with coverage marks in the gutter: the lines of getProductById that ran are green, the throw of ProductNotFoundException is red](https://ngvoicu.dev/articles/what-is-and-how-do-we-measure-code-coverage/images/coverage2.png)

Covered lines are green and uncovered are red.

Gabriel Voicu

I’m a software engineer. I build AI agents that work inside large systems, and I write open-source tools for coding agents.

[More about me](https://ngvoicu.dev/about/)
