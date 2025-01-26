import os
import hashlib
import pickle


def init_vcs():
    os.makedirs('.vcs_Storage', exist_ok=True)  # Corrected directory name
    print('VCS initialized.')


def snapshot(directory):
    snapshot_hash = hashlib.sha256()
    snapshot_data = {'files': {}}

    for root, dirs, files in os.walk(directory):
        # Skip the .vcs_Storage directory
        if '.vcs_Storage' in os.path.normpath(root):
            continue

        for file in files:
            file_path = os.path.join(root, file)

            try:
                with open(file_path, 'rb') as f:  # Use 'rb' for reading binary content
                    content = f.read()
                    snapshot_hash.update(content)
                    snapshot_data['files'][file_path] = content
            except (OSError, IOError) as e:
                print(f"Error reading {file_path}: {e}")

    hash_digest = snapshot_hash.hexdigest()
    snapshot_data['file_list'] = list(snapshot_data['files'].keys())

    # Save the snapshot data
    with open(f'.vcs_Storage/{hash_digest}', 'wb') as f:
        pickle.dump(snapshot_data, f)

    print(f'Snapshot created with hash: {hash_digest}')


def revert_to_snapshot(hash_digest):
    snapshot_path = f'.vcs_Storage/{hash_digest}'
    if not os.path.exists(snapshot_path):
        print('Snapshot does not exist.')
        return

    with open(snapshot_path, 'rb') as f:
        snapshot_data = pickle.load(f)

    # Restore files from the snapshot
    for file_path, content in snapshot_data['files'].items():
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(content)

    # Collect current files in the working directory
    current_files = set()
    for root, dirs, files in os.walk('.', topdown=True):
        if '.vcs_Storage' in os.path.normpath(root):
            continue
        for file in files:
            current_files.add(os.path.normpath(os.path.join(root, file)))

    # Identify files to delete
    snapshot_files = set(map(os.path.normpath, snapshot_data['file_list']))
    files_to_delete = current_files - snapshot_files

    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            print(f'Removed {file_path}')
        except (OSError, IOError) as e:
            print(f"Error removing {file_path}: {e}")

    print(f'Reverted to snapshot: {hash_digest}')


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python script.py [init|snapshot|revert] [snapshot_hash]')
        sys.exit(1)

    command = sys.argv[1]

    if command == 'init':
        init_vcs()
    elif command == 'snapshot':
        snapshot('.')  # Default to current directory
    elif command == 'revert':
        if len(sys.argv) < 3:
            print('Usage: python script.py revert [snapshot_hash]')
        else:
            revert_to_snapshot(sys.argv[2])
    else:
        print('Unknown command!')
