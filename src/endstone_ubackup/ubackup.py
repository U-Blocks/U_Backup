import os
import json
import time
import shutil
import zipfile
import datetime
import threading

from endstone.plugin import Plugin
from endstone import ColorFormat, Player
from endstone.command import Command, CommandSender
from endstone.scheduler import Task
from endstone.form import ActionForm

from endstone_ubackup.lang import load_langs

current_dir = os.getcwd()

first_dir = os.path.join(current_dir, 'plugins', 'ubackup')

if not os.path.exists(first_dir):
    os.mkdir(first_dir)

backups_dir = os.path.join(first_dir, 'backups')

if not os.path.exists(backups_dir):
    os.mkdir(backups_dir)

langs_dir = os.path.join(first_dir, 'langs')

if not os.path.exists(langs_dir):
    os.mkdir(langs_dir)

config_data_file_path = os.path.join(first_dir, 'config.json')


class ubackup(Plugin):
    api_version = '0.7'

    def __init__(self):
        super().__init__()

        if not os.path.exists(config_data_file_path):
            config_data = {
                'schedule_backup_time': [
                    '00:00:00',
                    '6:00:00',
                    '12:00:00',
                    '18:00:00'
                ],
                'max_backups_num': 3
            }

            with open(config_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(
                    config_data,
                    indent=4,
                    ensure_ascii=False
                )

                f.write(json_str)
        else:
            with open(config_data_file_path, 'r', encoding='utf-8') as f:
                config_data = json.loads(f.read())

        self.config_data = config_data

        self.langs = load_langs(langs_dir)

        self.ongoing_backup_info = {}

        self.backup_complete_broadcast_info = []

    def on_enable(self):
        self.logger.info(
            f'{ColorFormat.YELLOW}'
            f'U-Backup is enabled...'
        )

        self.server.scheduler.run_task(self, self.schedule_backup, delay=0, period=20)

    commands = {
        'ub': {
            'description': 'Call out the main form of U-Backup...',
            'usages': ['/ub'],
            'permissions': ['ubackup.command.ub']
        }
    }

    permissions = {
        'ubackup.command.ub': {
            'description': 'Call out the main form of U-Backup...',
            'default': 'OP'
        }
    }

    def on_command(self, sender: CommandSender, command: Command, args: list[str]):
        if not isinstance(sender, Player):
            self.logger.info(
                f'{ColorFormat.YELLOW}'
                f'This command can only be executed by a player...'
            )

            return

        player = sender

        if command.name == 'ub':
            main_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "main_form.title")}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "main_form.content")}'
            )

            main_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "main_form.button.manual_backup")}',
                icon='textures/ui/backup_replace',
                on_click=self.manual_backup
            )

            main_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "main_form.button.reload_configurations")}',
                icon='textures/ui/icon_setting',
                on_click=self.reload_configurations
            )

            if not self.server.plugin_manager.get_plugin('zx_ui'):
                main_form.on_close = None

                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.close")}',
                    icon='textures/ui/cancel',
                    on_click=None
                )
            else:
                main_form.on_close = self.back_to_zx_ui

                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.back_to_zx_ui")}',
                    icon='textures/ui/refresh_light',
                    on_click=self.back_to_zx_ui
                )

            player.send_form(main_form)

    def manual_backup(self, player: Player):
        if len(self.ongoing_backup_info) != 0:
            player.send_message(
                f'{ColorFormat.RED}'
                f'{self.get_text(player, "manual_backup.message.fail")}: '
                f'{ColorFormat.WHITE}'
                f'{self.get_text(player, "manual_backup.message.fail.reason1")}'
            )

            return

        if not self.check():
            player.send_message(
                f'{ColorFormat.RED}'
                f'{self.get_text(player, "manual_backup.message.fail")}: '
                f'{ColorFormat.WHITE}'
                f'{self.get_text(player, "manual_backup.message.fail.reason2")}'
            )

            return

        backup_start_time = time.time()

        datetime_now = str(datetime.datetime.now()).split('.')[0].split(' ')

        time_now = datetime_now[1].split(':')

        backup_datetime = datetime_now[0] + '-' + time_now[0] + '-' + time_now[1] + '-' + time_now[2]

        self.ongoing_backup_info = {
            'backup_start_time': backup_start_time,
            'backup_datetime': backup_datetime,
            'backup_type': 'manual'
        }

        threading.Thread(target=self.on_backup_thread).start()

        # Broadcast
        for online_player in self.server.online_players:
            if online_player.is_op:
                online_player.send_message(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(online_player, "manual_backup.broadcast.start")}'
                )

    def schedule_backup(self):
        datetime_now = str(datetime.datetime.now()).split('.')[0].split(' ')

        time_now = datetime_now[1]

        for sbt in self.config_data['schedule_backup_time']:
            if time_now == sbt:
                if len(self.ongoing_backup_info) != 0:
                    for online_player in self.server.online_players:
                        if online_player.is_op:
                            online_player.send_message(
                                f'{ColorFormat.RED}' +
                                self.get_text(online_player, "schedule_backup.broadcast.fail").format(time_now) +
                                f': '
                                f'{ColorFormat.WHITE}'
                                f'{self.get_text(online_player, "schedule_backup.broadcast.fail.reason1")}'
                            )

                    return

                if not self.check():
                    for online_player in self.server.online_players:
                        if online_player.is_op:
                            online_player.send_message(
                                f'{ColorFormat.RED}' +
                                self.get_text(online_player, "schedule_backup.broadcast.fail").format(time_now) +
                                f': '
                                f'{ColorFormat.WHITE}'
                                f'{self.get_text(online_player, "schedule_backup.broadcast.fail.reason2")}'
                            )

                    return

                time_now_re = time_now.split(':')

                backup_datetime = datetime_now[0] + '-' + time_now_re[0] + '-' + time_now_re[1] + '-' + time_now_re[2]

                backup_start_time = time.time()

                self.ongoing_backup_info = {
                    'backup_datetime': backup_datetime,
                    'backup_start_time': backup_start_time,
                    'backup_type': 'schedule',
                    'time_now': time_now
                }

                threading.Thread(target=self.on_backup_thread).start()

                for online_player in self.server.online_players:
                    if online_player.is_op:
                        online_player.send_message(
                            f'{ColorFormat.YELLOW}' +
                            self.get_text(online_player, "schedule_backup.broadcast.start").format(time_now)
                        )

                break

    def check(self):
        worlds_file_path = os.path.join(current_dir, 'worlds')

        worlds_size = 0

        for root, dirs, files in os.walk(worlds_file_path):
            for file in files:
                file_path = os.path.join(root, file)

                if not os.path.exists(file_path):
                    pass
                else:
                    worlds_size += os.path.getsize(file_path)

        if len(os.listdir(backups_dir)) >= self.config_data['max_backups_num']:
            over_num = len(os.listdir(backups_dir)) - self.config_data['max_backups_num'] + 1

            exist_backups = []

            for exist_backup in os.listdir(backups_dir):
                exist_backup_file_path = os.path.join(backups_dir, exist_backup)

                exist_backups.append(
                    [
                        os.path.getsize(exist_backup_file_path),
                        os.path.getctime(exist_backup_file_path)
                    ]
                )

            exist_backups.sort(key=lambda x: x[1], reverse=False)

            free_size = shutil.disk_usage(backups_dir).free

            for i in range(over_num):
                free_size += exist_backups[i][0]
        else:
            free_size = shutil.disk_usage(backups_dir).free

        if worlds_size > free_size:
            return False
        else:
            return True

    def on_backup_thread(self):
        if len(os.listdir(backups_dir)) >= self.config_data['max_backups_num']:
            over_num = len(os.listdir(backups_dir)) - self.config_data['max_backups_num'] + 1

            exist_backups = []

            for exist_backup in os.listdir(backups_dir):
                exist_backup_file_path = os.path.join(backups_dir, exist_backup)

                exist_backups.append(
                    [
                        exist_backup_file_path,
                        os.path.getctime(exist_backup_file_path)
                    ]
                )

            exist_backups.sort(key=lambda x: x[1], reverse=False)

            for i in range(over_num):
                os.remove(exist_backups[i][0])

        backup_zip_file_path = os.path.join(backups_dir, self.ongoing_backup_info['backup_datetime'] + '.zip')

        worlds_file_path = os.path.join(current_dir, 'worlds')

        with zipfile.ZipFile(backup_zip_file_path, 'w') as zipf:
            for root, dirs, files in os.walk(worlds_file_path):
                for file in files:
                    file_path = os.path.join(root, file)

                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.relpath(file_path, worlds_file_path))
                    else:
                        pass

        backup_complete_time = time.time()

        backup_expense_time = backup_complete_time - self.ongoing_backup_info['backup_start_time']

        time_units = ['s', 'm', 'h']
        time_unit_index = 0
        while backup_expense_time >= 60 and time_unit_index < len(time_units)-1:
            backup_expense_time /= 60
            time_unit_index += 1

        backup_zip_size = os.path.getsize(backup_zip_file_path)

        size_units = ['B', 'KB', 'MB', 'GB', 'TB']
        size_unit_index = 0
        while backup_zip_size >= 1024 and size_unit_index < len(size_units)-1:
            backup_zip_size /= 1024
            size_unit_index += 1

        task = self.server.scheduler.run_task(self, self.backup_complete_broadcast, delay=20, period=0)

        self.backup_complete_broadcast_info = [
            task,
            backup_expense_time,
            time_units,
            time_unit_index,
            backup_zip_size,
            size_units,
            size_unit_index
        ]

    def backup_complete_broadcast(self):
        task: Task = self.backup_complete_broadcast_info[0]

        backup_expense_time = self.backup_complete_broadcast_info[1]
        time_units = self.backup_complete_broadcast_info[2]
        time_unit_index = self.backup_complete_broadcast_info[3]

        backup_zip_size = self.backup_complete_broadcast_info[4]
        size_units = self.backup_complete_broadcast_info[5]
        size_unit_index = self.backup_complete_broadcast_info[6]

        for online_player in self.server.online_players:
            if online_player.is_op:
                if self.ongoing_backup_info['backup_type'] == 'manual':
                    online_player.send_message(
                        f'{ColorFormat.YELLOW}'
                        f'{self.get_text(online_player, "manual_backup.broadcast.complete")}\n'
                        f'{self.get_text(online_player, "time_expense")}: '
                        f'{ColorFormat.WHITE}'
                        f'{round(backup_expense_time, 2)} {time_units[time_unit_index]}\n'
                        f'{ColorFormat.YELLOW}'
                        f'{self.get_text(online_player, "size")}: '
                        f'{ColorFormat.WHITE}'
                        f'{round(backup_zip_size, 2)} {size_units[size_unit_index]}'
                    )
                else:
                    time_now = self.ongoing_backup_info['time_now']

                    online_player.send_message(
                        f'{ColorFormat.YELLOW}' +
                        self.get_text(online_player, "schedule_backup.broadcast.complete").format(time_now) + '\n'
                        f'{self.get_text(online_player, "time_expense")}: '
                        f'{ColorFormat.WHITE}'
                        f'{round(backup_expense_time, 2)} {time_units[time_unit_index]}\n'
                        f'{ColorFormat.YELLOW}'
                        f'{self.get_text(online_player, "size")}: '
                        f'{ColorFormat.WHITE}'
                        f'{round(backup_zip_size, 2)} {size_units[size_unit_index]}'
                    )

        self.server.scheduler.cancel_task(task.task_id)

        self.backup_complete_broadcast_info = []

        self.ongoing_backup_info = {}

    def reload_configurations(self, player: Player):
        reload_configurations_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "reload_configurations_from.title")}',
            on_close=self.back_to_main_form
        )

        content = (f'{ColorFormat.GREEN}'
                   f'{self.get_text(player, "reload_configurations_from.content1")}\n'
                   f'{ColorFormat.WHITE}')

        for bt in self.config_data['schedule_backup_time']:
            content += f'{bt}\n'

        content += (f'\n'
                    f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "reload_configurations_from.content2")}: '
                    f'{ColorFormat.WHITE}'
                    f'{self.config_data["max_backups_num"]}\n'
                    f'\n'
                    f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "reload_configurations_from.content3")}')

        reload_configurations_form.content = content

        reload_configurations_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "reload_configurations_from.button.reload")}',
            icon='textures/ui/icon_setting',
            on_click=self.reload_config_data
        )

        reload_configurations_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "back")}',
            icon='textures/ui/refresh_light',
            on_click=self.back_to_main_form
        )

        player.send_form(reload_configurations_form)

    def reload_config_data(self, player: Player):
        with open(config_data_file_path, 'r', encoding='utf-8') as f:
            self.config_data = json.loads(f.read())

        player.send_message(f'{ColorFormat.YELLOW}'
                            f'{self.get_text(player, "reload_configurations.message.success")}')

    def back_to_main_form(self, player: Player):
        player.perform_command('ub')

    def back_to_zx_ui(self, player: Player):
        player.perform_command('cd')

    def get_text(self, player: Player, text_key: str) -> str:
        player_lang = player.locale

        try:
            if self.langs.get(player_lang) is None:
                text_value = self.langs['en_US'][text_key]
            else:
                if self.langs[player_lang].get(text_key) is None:
                    text_value = self.langs['en_US'][text_key]
                else:
                    text_value = self.langs[player_lang][text_key]

            return text_value
        except Exception as e:
            self.logger.error(
                f'{ColorFormat.RED}'
                f'{e}'
            )

            return text_key
