# This file contains the boilerplate/starter code snippets for various languages.
# The keys should match the 'value' attributes from the <option> tags in the HTML.

STARTER_CODE = {
    "python": """def main():
    # Your code here
    print("Hello, Python!")

if __name__ == "__main__":
    main()
""",
    "text/x-java": """public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, Java!");
    }
}
""",
    "text/x-c++src": """#include <iostream>

int main() {
    std::cout << "Hello, C++!" << std::endl;
    return 0;
}
""",
    "text/x-csrc": """#include <stdio.h>

int main() {
    printf("Hello, C!\\n");
    return 0;
}
""",
    "javascript": """// Your code here
console.log("Hello, JavaScript!");
""",
    "htmlmixed": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    
</body>
</html>
""",
    "css": """/* Your CSS styles here */
body {
    font-family: sans-serif;
}
""",
    "ruby": """# Your Ruby code here
puts "Hello, Ruby!"
""",
    "text/x-kotlin": """fun main() {
    println("Hello, Kotlin!")
}
""",
    "sql": """-- Your SQL query here
SELECT * FROM users;
"""
}
