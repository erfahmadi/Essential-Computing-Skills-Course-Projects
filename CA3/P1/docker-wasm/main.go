package main

import "fmt"

func main() {
    fmt.Println("Hello from Go compiled to WebAssembly!")
    
    a, b := 5, 7
    sum := a + b
    fmt.Printf("The sum of %d and %d is %d\n", a, b, sum)
}
