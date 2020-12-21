using Microsoft.VisualStudio.TestTools.UnitTesting;
using view.getters;

namespace viewTests
{
    [TestClass]
    public class viewTest
    {
        [TestMethod]
        public void TestLogGetter()
        {
            LogGetter logGetter = new LogGetter();
            logGetter.Get();
        }
    }
}
