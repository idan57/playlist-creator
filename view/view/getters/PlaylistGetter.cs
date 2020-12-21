using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;

namespace view.getters
{
    public class PlaylistGetter : Getter
    {
        private string runArgs;
        public PlaylistGetter(string args)
        {
            runArgs = args;
        }

        public string Get()
        {
            bool status = RunPlaylistCreation();
            if (status)
            {
                return ParsePlaylist();
            }
            else
            {
                return "$$FAILURE$$";
            }
        }

        private string ParsePlaylist()
        {
            throw new NotImplementedException();
        }

        private bool RunPlaylistCreation()
        {
            Process process = new Process();
            process.StartInfo.FileName = "python.exe";
            process.StartInfo.Arguments = runArgs;
            process.Start();
            process.WaitForExit();
            return process.ExitCode == 0;
        }
    }
}
