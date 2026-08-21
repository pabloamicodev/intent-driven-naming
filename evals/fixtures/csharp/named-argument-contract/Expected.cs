using System;

public sealed class PaymentProcessor
{
    public string Process(string id) => id;
}

public static class Program
{
    public static void Main()
    {
        var processor = new PaymentProcessor();
        Console.Write(processor.Process(id: "pay-123"));
    }
}
