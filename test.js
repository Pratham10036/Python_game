function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomArray(length) {
  return Array.from({ length }, () => getRandomInt(1, 100));
}

const arr = randomArray(10);
console.log("Random array:", arr);
console.log(
  "Sum:",
  arr.reduce((a, b) => a + b, 0)
);

const fruits = ["apple", "banana", "cherry", "date"];
console.log("Random fruit:", fruits[getRandomInt(0, fruits.length - 1)]);

for (let i = 0; i < 3; i++) {
  console.log(`Random int ${i + 1}:`, getRandomInt(1, 50));
}
