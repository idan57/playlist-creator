using System.IO;

namespace view.getters
{
    public class LogGetter : Getter
    {
        public string Get()
        {
            string curr_dir = Directory.GetCurrentDirectory();
            string log_path = Path.GetFullPath(Path.Combine(curr_dir, "..\\..\\..\\..\\..\\logs\\current\\log.txt"));
            StreamReader sr = File.OpenText(log_path);
            string log = sr.ReadToEnd();
            sr.Close();
            return log;
        }
    }
}
