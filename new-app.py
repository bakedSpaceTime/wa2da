from pathlib import Path
import subprocess
import os
import shutil

SCRIPT_DIR = Path(__file__).parent

DISTROBOX_BIN_DIR = Path("/") / "usr" / "bin"
HOST_BIN_DIR = Path.home() / ".local" / "bin"

HOST_DESKTOP_DIR = Path.home() / ".local" / "share" / "applications"
HOST_DESKTOP_ICON_DIR = Path.home() / ".local" / "share" / "icons" / "distrobox"


class App:
    def __init__(self, name, description, icon: Path, categories, web_app_url):
        self.name = name.lower()
        self.description = description
        self.icon = icon
        self.categories = categories
        self.web_app_url = web_app_url

        self._temp_directory = SCRIPT_DIR / self.name

        self._distrobox_bin_root = DISTROBOX_BIN_DIR / self.name
        self._host_bin_root = HOST_BIN_DIR / self.name

        os.makedirs(self._temp_directory, exist_ok=True)

    @property
    def title(self):
        return self.name.title()

    @property
    def pake_deb_file_path(self):
        return self._temp_directory / Path(self.name).with_suffix(".deb")

    @property
    def desktop_file_path(self):
        return HOST_DESKTOP_DIR / f"ubuntu24lts-{self.name}.desktop"

    @property
    def desktop_icon_file_path(self):
        return HOST_DESKTOP_ICON_DIR / f"{self.name}-desktop.png"

    @property
    def temp_desktop_file_path(self):
        return self._temp_directory / f"ubuntu24lts-{self.name}.desktop"

    @property
    def distrobox_bin_file_path(self):
        return self._distrobox_bin_root / "usr" / "bin" / "pake"

    @property
    def host_bin_file_path(self):
        return self._host_bin_root / "pake"

    def template_desktop_file(self: "App") -> str:

        template = f"""[Desktop Entry]
Name={self.title} (on ubuntu24lts)
Exec={self.host_bin_file_path}
Terminal=false
Type=Application
Icon={self.desktop_icon_file_path}
StartupWMClass={self.title}
Comment={self.description}
Categories={self.categories}
"""
        return template

    def pake_build(self: "App") -> bool:
        os.chdir(self._temp_directory)

        cmd = [
            "pake",
            self.web_app_url,
            "--name",
            self.name,
            "--width",
            "1920",
            "--height",
            "1080",
            "--icon",
            str(self.icon),
            # "--help",
        ]
        print(cmd)
        result = subprocess.run(cmd)

        # Check if the command was successful
        success = result.returncode == 0
        if success:
            print(f"Successfully created {self.name} app.")
        else:
            print(f"Failed to create {self.name} app.")

        os.chdir(SCRIPT_DIR)

        return success

    def distrobox_install(self: "App") -> bool:

        cmd = [
            "distrobox-enter",
            "ubuntu24lts",
            "--",
            "sudo",
            "dpkg",
            "-x",
            str(self.pake_deb_file_path),
            str(self._distrobox_bin_root),
        ]
        result = subprocess.run(cmd)

        # Check if the command was successful
        success = result.returncode == 0
        if success:
            print(f"Successfully installed {self.name} deb.")
        else:
            print(f"Failed to install {self.name} deb.")

        return success

    def distrobox_export(self: "App") -> bool:
        cmd = [
            "distrobox-enter",
            "ubuntu24lts",
            "--",
            "distrobox-export",
            "-b",
            str(self.distrobox_bin_file_path),
            "-el",
            self.name,
            "-ep",
            str(self._host_bin_root),
        ]
        print(cmd)
        result = subprocess.run(cmd)

        # Check if the command was successful
        success = result.returncode == 0
        if success:
            print(f"Successfully installed {self.name} deb.")
        else:
            print(f"Failed to install {self.name} deb.")

        return success

    def copy_icon(self: "App") -> bool:
        try:
            # Ensure the destination directory exists
            os.makedirs(HOST_DESKTOP_ICON_DIR, exist_ok=True)

            # Copy the icon file using shutil.copy2 to preserve metadata
            shutil.copy2(self.icon, HOST_DESKTOP_ICON_DIR)
            os.rename(
                HOST_DESKTOP_ICON_DIR / self.icon.name,
                self.desktop_icon_file_path,
            )
            print(f"Successfully copied icon for {self.name}")
            return True
        except Exception as e:
            print(f"Failed to copy icon for {self.name}: {str(e)}")
            return False

    def install(self: "App") -> bool:
        self.pake_build()
        self.distrobox_install()
        self.distrobox_export()
        self.copy_icon()

        with open(self.temp_desktop_file_path, "w") as f:
            f.write(self.template_desktop_file())

        with open(self.desktop_file_path, "w") as f:
            f.write(self.template_desktop_file())


if __name__ == "__main__":
    app = App(
        name="Fastmail",
        description="Email and calendar made better",
        icon="/home/your-user/.local/share/icons/distrobox/fastmail-desktop.png",
        command="/home/your-user/.local/bin/fastmail/pake",
        categories="Mail;Organization;",
        web_app_url="https://app.fastmail.com/mail/",
    )
    # app = App(
    #     name="Claude",
    #     description="Claude AI",
    #     icon=Path("/home/your-user/Pictures/icons/claude-color.png"),
    #     categories="AI;Organization;",
    #     web_app_url="https://claude.ai/new",
    # )

    app.install()
