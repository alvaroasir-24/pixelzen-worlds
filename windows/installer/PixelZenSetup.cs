using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Win32;

namespace PixelZenSetup {
    internal static class Program {
        [STAThread]
        static void Main(string[] args) {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            foreach (string a in args) {
                if (string.Equals(a, "--uninstall", StringComparison.OrdinalIgnoreCase)) {
                    EjecutarDesinstalacion();
                    return;
                }
            }
            Application.Run(new SetupForm());
        }

        static string GetRootInstallDir() {
            return Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "PixelZenWorlds"
            );
        }

        static void KillPidFile(string fileName) {
            try {
                string path = Path.Combine(Path.GetTempPath(), fileName);
                if (!File.Exists(path)) return;
                string txt = File.ReadAllText(path).Trim();
                int pid;
                if (int.TryParse(txt, out pid)) {
                    try {
                        var p = Process.GetProcessById(pid);
                        p.Kill();
                    } catch { }
                }
                File.Delete(path);
            } catch { }
        }

        internal static void DetenerInstanciasActivas() {
            KillPidFile("pixelzen_app.pid");
            KillPidFile("pixelzen_hud.pid");
            KillPidFile("pixelzen_win.pid");
            KillPidFile("pixelzen_srv.pid");
        }

        static void EjecutarDesinstalacion() {
            var res = MessageBox.Show(
                "¿Seguro que quieres desinstalar PixelZen Worlds?\nSe cerrarán las cajitas/ciclo activo y se quitarán los accesos directos.",
                "Desinstalar PixelZen Worlds",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question
            );
            if (res != DialogResult.Yes) return;

            DetenerInstanciasActivas();

            try {
                using (var runKey = Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\Windows\CurrentVersion\Run", true)) {
                    if (runKey != null) runKey.DeleteValue("PixelZenWorlds", false);
                }
            } catch { }

            try {
                Registry.CurrentUser.DeleteSubKeyTree(@"Software\Microsoft\Windows\CurrentVersion\Uninstall\PixelZenWorlds", false);
            } catch { }

            string desk = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
            string start = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Programs), "PixelZen Worlds.lnk");
            string deskLnk = Path.Combine(desk, "PixelZen Worlds.lnk");
            try { if (File.Exists(deskLnk)) File.Delete(deskLnk); } catch { }
            try { if (File.Exists(start)) File.Delete(start); } catch { }

            string root = GetRootInstallDir();
            try {
                string appDir = Path.Combine(root, "app");
                if (Directory.Exists(appDir)) Directory.Delete(appDir, true);
            } catch { }

            try {
                string cmdArgs = string.Format("/c ping 127.0.0.1 -n 3 >nul & rmdir /s /q \"{0}\"", root);
                Process.Start(new ProcessStartInfo {
                    FileName = "cmd.exe",
                    Arguments = cmdArgs,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WindowStyle = ProcessWindowStyle.Hidden
                });
            } catch { }

            MessageBox.Show(
                "PixelZen Worlds ha sido desinstalado correctamente.",
                "PixelZen Worlds",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
    }

    internal class SetupForm : Form {
        private readonly CheckBox chkDesk;
        private readonly CheckBox chkStart;
        private readonly CheckBox chkAuto;
        private readonly ProgressBar bar;
        private readonly Label lblStatus;
        private readonly Button btnInstall;

        public SetupForm() {
            Text = "Instalador · PixelZen Worlds";
            ClientSize = new Size(520, 390);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = Color.FromArgb(11, 16, 32);
            ForeColor = Color.FromArgb(243, 234, 214);
            try { Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath); } catch { }

            var lblTitle = new Label {
                Text = "✦ PIXELZEN WORLDS",
                Font = new Font("Segoe UI", 16, FontStyle.Bold),
                ForeColor = Color.FromArgb(84, 222, 212),
                Location = new Point(28, 24),
                AutoSize = true
            };
            var lblSub = new Label {
                Text = "Fondos pixel art animados con ciclo solar, soporte de 1 o 2 monitores\ny panel HUD en el escritorio. Sin configurar código ni ver carpetas.",
                Font = new Font("Segoe UI", 9.5f),
                ForeColor = Color.FromArgb(168, 184, 207),
                Location = new Point(30, 62),
                Size = new Size(460, 44)
            };

            string root = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "PixelZenWorlds"
            );
            var lblDest = new Label {
                Text = "Se instalará limpiamente en:\n" + Path.Combine(root, "app"),
                Font = new Font("Consolas", 8.5f),
                ForeColor = Color.FromArgb(143, 168, 198),
                BackColor = Color.FromArgb(18, 28, 52),
                Padding = new Padding(10, 8, 10, 8),
                Location = new Point(30, 118),
                Size = new Size(460, 50)
            };

            chkDesk = new CheckBox {
                Text = "Crear icono en el Escritorio (PixelZen Worlds)",
                Checked = true,
                ForeColor = ForeColor,
                Font = new Font("Segoe UI", 9.5f),
                Location = new Point(30, 184),
                AutoSize = true
            };
            chkStart = new CheckBox {
                Text = "Añadir al Menú Inicio de Windows",
                Checked = true,
                ForeColor = ForeColor,
                Font = new Font("Segoe UI", 9.5f),
                Location = new Point(30, 212),
                AutoSize = true
            };
            chkAuto = new CheckBox {
                Text = "Iniciar en segundo plano al encender Windows",
                Checked = false,
                ForeColor = ForeColor,
                Font = new Font("Segoe UI", 9.5f),
                Location = new Point(30, 240),
                AutoSize = true
            };

            bar = new ProgressBar {
                Location = new Point(30, 280),
                Size = new Size(460, 16),
                Style = ProgressBarStyle.Continuous,
                Minimum = 0,
                Maximum = 100
            };

            lblStatus = new Label {
                Text = "Listo para instalar. No requiere Python ni dependencias externas.",
                Font = new Font("Segoe UI", 9f),
                ForeColor = Color.FromArgb(168, 184, 207),
                Location = new Point(30, 304),
                Size = new Size(460, 20)
            };

            btnInstall = new Button {
                Text = "Instalar y abrir",
                Font = new Font("Segoe UI", 10f, FontStyle.Bold),
                BackColor = Color.FromArgb(24, 62, 70),
                ForeColor = Color.FromArgb(243, 234, 214),
                FlatStyle = FlatStyle.Flat,
                Location = new Point(320, 336),
                Size = new Size(170, 36)
            };
            btnInstall.FlatAppearance.BorderColor = Color.FromArgb(84, 222, 212);
            btnInstall.Click += async (s, e) => await InstalarAsync();

            var btnCancel = new Button {
                Text = "Cancelar",
                Font = new Font("Segoe UI", 9.5f),
                BackColor = Color.FromArgb(18, 28, 52),
                ForeColor = Color.FromArgb(168, 184, 207),
                FlatStyle = FlatStyle.Flat,
                Location = new Point(214, 336),
                Size = new Size(96, 36)
            };
            btnCancel.FlatAppearance.BorderColor = Color.FromArgb(47, 66, 102);
            btnCancel.Click += (s, e) => Close();

            Controls.AddRange(new Control[] {
                lblTitle, lblSub, lblDest, chkDesk, chkStart, chkAuto, bar, lblStatus, btnCancel, btnInstall
            });
        }

        private void CrearAcceso(string lnkPath, string targetVbs, string workDir, string iconPath) {
            string ps = string.Format(
                "$ws = New-Object -ComObject WScript.Shell; " +
                "$sc = $ws.CreateShortcut('{0}'); " +
                "$sc.TargetPath = 'wscript.exe'; " +
                "$sc.Arguments = '\"{1}\"'; " +
                "$sc.WorkingDirectory = '{2}'; " +
                "$sc.Description = 'PixelZen Worlds (Fondos animados, multimonitor y HUD)'; " +
                "$sc.IconLocation = '{3}'; " +
                "$sc.Save()",
                lnkPath.Replace("'", "''"),
                targetVbs.Replace("'", "''"),
                workDir.Replace("'", "''"),
                iconPath.Replace("'", "''")
            );
            var psi = new ProcessStartInfo {
                FileName = "powershell.exe",
                Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command \"" + ps.Replace("\"", "\\\"") + "\"",
                UseShellExecute = false,
                CreateNoWindow = true,
                WindowStyle = ProcessWindowStyle.Hidden
            };
            using (var p = Process.Start(psi)) {
                if (p != null) p.WaitForExit(10000);
            }
        }

        private async Task InstalarAsync() {
            btnInstall.Enabled = false;
            bool mkDesk = chkDesk.Checked;
            bool mkStart = chkStart.Checked;
            bool mkAuto = chkAuto.Checked;

            lblStatus.Text = "Preparando instalación...";
            bar.Value = 15;

            string root = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "PixelZenWorlds"
            );
            string appDir = Path.Combine(root, "app");
            string vbsLauncher = Path.Combine(appDir, "PixelZenApp.vbs");
            string uninstPs = Path.Combine(appDir, "Desinstalar.ps1");
            string icoPath = Path.Combine(appDir, "pixelzen.ico");

            try {
                await Task.Run(() => {
                    Program.DetenerInstanciasActivas();
                    Directory.CreateDirectory(root);
                    if (Directory.Exists(appDir)) Directory.Delete(appDir, true);
                    Directory.CreateDirectory(appDir);

                    var asm = Assembly.GetExecutingAssembly();
                    using (var stream = asm.GetManifestResourceStream("PixelZenPayload.zip")) {
                        if (stream == null) throw new InvalidOperationException("No se encontró el paquete interno PixelZenPayload.zip.");
                        string tmpZip = Path.Combine(Path.GetTempPath(), "pixelzen_payload_" + Guid.NewGuid().ToString("N") + ".zip");
                        try {
                            using (var fs = File.Create(tmpZip)) stream.CopyTo(fs);
                            ZipFile.ExtractToDirectory(tmpZip, appDir);
                        } finally {
                            if (File.Exists(tmpZip)) File.Delete(tmpZip);
                        }
                    }
                });

                bar.Value = 70;
                lblStatus.Text = "Creando accesos directos...";

                await Task.Run(() => {
                    if (mkDesk) {
                        string deskLnk = Path.Combine(
                            Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory),
                            "PixelZen Worlds.lnk"
                        );
                        CrearAcceso(deskLnk, vbsLauncher, appDir, icoPath);
                    }
                    if (mkStart) {
                        string progDir = Environment.GetFolderPath(Environment.SpecialFolder.Programs);
                        Directory.CreateDirectory(progDir);
                        string startLnk = Path.Combine(progDir, "PixelZen Worlds.lnk");
                        CrearAcceso(startLnk, vbsLauncher, appDir, icoPath);
                    }
                    if (mkAuto) {
                        using (var runKey = Registry.CurrentUser.CreateSubKey(@"Software\Microsoft\Windows\CurrentVersion\Run")) {
                            if (runKey != null) runKey.SetValue("PixelZenWorlds", string.Format("wscript.exe \"{0}\" --tray", vbsLauncher));
                        }
                    }

                    string appVersion = "1.0.0";
                    string verFile = Path.Combine(appDir, "VERSION");
                    if (File.Exists(verFile)) {
                        string txt = File.ReadAllText(verFile).Trim();
                        if (!string.IsNullOrEmpty(txt)) appVersion = txt;
                    }

                    using (var unKey = Registry.CurrentUser.CreateSubKey(@"Software\Microsoft\Windows\CurrentVersion\Uninstall\PixelZenWorlds")) {
                        if (unKey != null) {
                            unKey.SetValue("DisplayName", "PixelZen Worlds");
                            unKey.SetValue("DisplayVersion", appVersion);
                            unKey.SetValue("Publisher", "PixelZen Worlds");
                            unKey.SetValue("DisplayIcon", icoPath);
                            unKey.SetValue("InstallLocation", appDir);
                            unKey.SetValue("UninstallString", string.Format("powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \"{0}\"", uninstPs));
                            unKey.SetValue("NoModify", 1, RegistryValueKind.DWord);
                            unKey.SetValue("NoRepair", 1, RegistryValueKind.DWord);
                        }
                    }
                });

                bar.Value = 100;
                lblStatus.Text = "¡Instalado! Abriendo PixelZen Worlds...";

                Process.Start(new ProcessStartInfo {
                    FileName = "wscript.exe",
                    Arguments = string.Format("\"{0}\"", vbsLauncher),
                    WorkingDirectory = appDir,
                    UseShellExecute = false,
                    CreateNoWindow = true
                });

                await Task.Delay(500);
                Close();
            } catch (Exception ex) {
                btnInstall.Enabled = true;
                bar.Value = 0;
                lblStatus.Text = "Error al instalar.";
                MessageBox.Show(
                    "No se pudo completar la instalación:\n" + ex.Message,
                    "Error · PixelZen Worlds",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }
    }
}
