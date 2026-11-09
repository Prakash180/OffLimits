# Java Cheat Sheet: Primitive, Wrapper, and Collections

Quick revision notes with ready-to-use syntax.

---

## 1) Primitive vs Non-Primitive (Wrapper)

### Primitive types
- `byte`, `short`, `int`, `long`
- `float`, `double`
- `char`, `boolean`

### Wrapper (non-primitive) types
- `Byte`, `Short`, `Integer`, `Long`
- `Float`, `Double`
- `Character`, `Boolean`

---

## 2) Primitive <-> Wrapper Conversion

### Auto-boxing (primitive -> wrapper)
```java
int a = 10;
Integer x = a;
```

### Auto-unboxing (wrapper -> primitive)
```java
Integer x = 20;
int a = x;
```

### Manual boxing (explicit)
```java
int a = 10;
Integer x = Integer.valueOf(a);
```

### Manual unboxing (explicit)
```java
Integer x = 20;
int a = x.intValue();
```

### Null safety note
```java
Integer x = null;
// int a = x; // NullPointerException (auto-unboxing null)
int a = (x != null) ? x : 0;
```

---

## 3) String <-> Primitive / Wrapper Conversion

### String -> primitive
```java
int i = Integer.parseInt("123");
long l = Long.parseLong("123");
double d = Double.parseDouble("12.5");
float f = Float.parseFloat("12.5");
short s = Short.parseShort("12");
byte b = Byte.parseByte("7");
boolean ok = Boolean.parseBoolean("true");
char c = "ABC".charAt(0); // 'A'
```

### String -> wrapper
```java
Integer i = Integer.valueOf("123");
Long l = Long.valueOf("123");
Double d = Double.valueOf("12.5");
Boolean ok = Boolean.valueOf("true");
Character c = Character.valueOf("ABC".charAt(0));
```

### Primitive/wrapper -> String
```java
String s1 = String.valueOf(123);        // primitive to String
String s2 = String.valueOf(12.5);       // primitive to String
String s3 = String.valueOf(true);       // primitive to String
String s4 = String.valueOf('A');        // char to String
String s5 = Integer.toString(123);      // wrapper utility method
String s6 = Double.toString(12.5);
```

---

## 4) Primitive Array -> Collection

### int[] -> List<Integer>
```java
int[] arr = {1, 2, 3};
List<Integer> list = java.util.Arrays.stream(arr)
    .boxed()
    .collect(java.util.stream.Collectors.toList());
```

### long[] -> List<Long>
```java
long[] arr = {1L, 2L, 3L};
List<Long> list = java.util.Arrays.stream(arr)
    .boxed()
    .collect(java.util.stream.Collectors.toList());
```

### double[] -> List<Double>
```java
double[] arr = {1.1, 2.2, 3.3};
List<Double> list = java.util.Arrays.stream(arr)
    .boxed()
    .collect(java.util.stream.Collectors.toList());
```

### int[] -> Set<Integer>
```java
int[] arr = {1, 2, 2, 3};
Set<Integer> set = java.util.Arrays.stream(arr)
    .boxed()
    .collect(java.util.stream.Collectors.toSet());
```

### Why not Arrays.asList(int[])?
```java
int[] arr = {1, 2, 3};
List<int[]> wrong = java.util.Arrays.asList(arr); // one element (the whole array)
```

---

## 5) Object Array (Wrapper/String) -> Collection

### Integer[] / String[] -> List
```java
Integer[] nums = {1, 2, 3};
List<Integer> list1 = java.util.Arrays.asList(nums);

String[] names = {"A", "B"};
List<String> list2 = java.util.Arrays.asList(names);
```

### Create mutable list
```java
List<Integer> mutable = new java.util.ArrayList<>(java.util.Arrays.asList(1, 2, 3));
```

### Array -> Set
```java
String[] names = {"A", "B", "A"};
Set<String> set = new java.util.HashSet<>(java.util.Arrays.asList(names));
```

---

## 6) Collection -> Primitive Array

### List<Integer> -> int[]
```java
List<Integer> list = java.util.Arrays.asList(1, 2, 3);
int[] arr = list.stream().mapToInt(Integer::intValue).toArray();
```

### List<Long> -> long[]
```java
List<Long> list = java.util.Arrays.asList(1L, 2L, 3L);
long[] arr = list.stream().mapToLong(Long::longValue).toArray();
```

### List<Double> -> double[]
```java
List<Double> list = java.util.Arrays.asList(1.1, 2.2, 3.3);
double[] arr = list.stream().mapToDouble(Double::doubleValue).toArray();
```

---

## 7) Collection -> Object Array

### List<Integer> -> Integer[]
```java
List<Integer> list = java.util.Arrays.asList(1, 2, 3);
Integer[] arr = list.toArray(new Integer[0]);
```

### List<String> -> String[]
```java
List<String> list = java.util.Arrays.asList("A", "B");
String[] arr = list.toArray(new String[0]);
```

---

## 8) Primitive/Wrapper -> List with Fixed Values

### Primitive literals to List<Integer>
```java
List<Integer> list = java.util.List.of(1, 2, 3);
```

### Wrapper objects to mutable list
```java
List<Integer> list = new java.util.ArrayList<>(java.util.List.of(1, 2, 3));
```

### String literals to list
```java
List<String> list = java.util.List.of("red", "green", "blue");
```

---

## 9) Build Map from Primitive/Wrapper Values

### Quick immutable map
```java
Map<Integer, String> map = java.util.Map.of(
    1, "one",
    2, "two"
);
```

### From arrays with loop
```java
int[] keys = {1, 2, 3};
String[] values = {"one", "two", "three"};

Map<Integer, String> map = new java.util.HashMap<>();
for (int i = 0; i < keys.length; i++) {
    map.put(keys[i], values[i]);
}
```

---

## 10) Quick Error-Safe Parse Pattern

```java
String raw = "123";
int value;
try {
    value = Integer.parseInt(raw);
} catch (NumberFormatException e) {
    value = 0; // fallback
}
```

Use this when input may not be a valid number.
