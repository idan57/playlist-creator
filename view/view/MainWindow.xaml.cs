using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using view.getters;

namespace view
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private Thread logThread;
        private Thread playlistCreatorThread;
        private LogGetter logGetter = new LogGetter();
        
        private string log;
        public string Log
        {
            get { return log;  }
            set
            {
                log = value;
                OnPropertyChanged();
            }
        }

        private string playlist;
        public string Playlist
        {
            get { return playlist; }
            set
            {
                playlist = value;
                OnPropertyChanged();
            }
        }

        public MainWindow()
        {
            DataContext = this;
            InitializeComponent();
        }
        public event PropertyChangedEventHandler PropertyChanged;
        private void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        private void Border_MouseDown(object sender, MouseButtonEventArgs e)
        {
            CheckNumOfFilled();
            RunPlaylistCreator();
        }

        private void CheckNumOfFilled()
        {
            int countFilled = 0;
            if (!albumsPath.Text.Equals(""))
            {
                countFilled++;
            }
            if (!artistsPath.Text.Equals(""))
            {
                countFilled++;
            }
            if (!songsPath.Text.Equals(""))
            {
                countFilled++;
            }
            if (!genresPath.Text.Equals(""))
            {
                countFilled++;
            }
            if (countFilled > 1)
            {
                new error($"You can't fill more than 1 value, you filled: {countFilled}");
            }
        }

        private void RunPlaylistCreator()
        {
            int countFilled = 0;
            string runArgs = GetRunningCommand();
            logThread = new Thread(SetLogData);
            playlistCreatorThread = new Thread(CreatePlaylist);
        }

        private void CreatePlaylist(object runArgs)
        {
            PlaylistGetter playlistGetter = new PlaylistGetter((string)runArgs);
            Playlist = playlistGetter.Get();
        }

        private string GetRunningCommand()
        {
            int minimumTime = int.Parse(minTime.Text);
            int maximunTime = int.Parse(maxTime.Text);
            string runArgs = "";
            if (!albumsPath.Text.Equals(""))
            {
                runArgs = $"-l {albumsPath.Text}";
            }
            if (!artistsPath.Text.Equals(""))
            {
                runArgs = $"-r {artistsPath.Text}";
            }
            if (!songsPath.Text.Equals(""))
            {
                if (songsPath.Text.Contains(","))
                {
                    string[] pathAndNum = songsPath.Text.Split(',');
                    runArgs = $"-s {pathAndNum[0]} -m {pathAndNum[0]}";
                }
                else
                {
                    runArgs = $"-s {songsPath.Text}";
                }
            }
            if (!genresPath.Text.Equals(""))
            {
                runArgs = $"-g {genresPath.Text}";
            }
            runArgs += " -d {minimumTime} -u {maximunTime}";
            return runArgs;
        }

        private void SetLogData()
        {
            while(!logGetter.IsDone())
            {
                Log = logGetter.Get();
                Thread.Sleep(1000);
            }
        }
    }
}
