using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace view.getters
{
    public class LogGetter : Getter
    {
        public string Get()
        {
            string curr_dir = Directory.GetCurrentDirectory();
            string log_path = Path.GetFullPath(Path.Combine(curr_dir, "..\\..\\..\\..\\..\\logs\\current\\temp_log.txt"));
            StreamReader sr = File.OpenText(log_path);
            string log = sr.ReadToEnd();
            sr.Close();
            TruncateTempLog(log_path);
            return log;
        }

        private void TruncateTempLog(string log_path)
        {
            FileStream truncateStream = new FileStream(log_path, FileMode.Truncate, FileAccess.ReadWrite);
            truncateStream.Close();
        }
    }
}
