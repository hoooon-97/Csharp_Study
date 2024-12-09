using System;

namespace MyProject
{
    class Program
    {
        static void Main(string[] args)
        {
            int X = int.Parse(Console.ReadLine());
            int Y = int.Parse(Console.ReadLine()); 
            int result = 0;

            if (X > 0 && Y > 0) {
                result = 1;
            } else if (X < 0 && Y > 0) {
                result = 2;
            } else if (X < 0 && Y < 0) {
                result = 3;
            } else if (X > 0 && Y < 0) {
                result = 4;
            }
            Console.WriteLine(result);
        }
    }
}