import 'dart:io';
import 'dart:ui';

import 'package:client/core/providers/current_user_notifier.dart';
import 'package:client/core/utils.dart';
import 'package:client/features/home/model/fav_song_model.dart';
import 'package:client/features/home/model/song_model.dart';
import 'package:client/features/home/repository/home_local_repository.dart';
import 'package:client/features/home/repository/home_repository.dart';
import 'package:fpdart/fpdart.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'home_view_model.g.dart';

@riverpod
Future<List<SongModel>> getFavSongs(GetFavSongsRef ref) async {
  final token =
      ref.watch(currentUserNotifierProvider.select((user) => user!.token));
  final res = await ref.watch(homeRepositoryProvider).getFavSongs(
        token: token,
      );

  return switch (res) {
    Left(value: final l) => throw l.message,
    Right(value: final r) => r,
  };
}

@riverpod
Future<List<SongModel>> getAllSongs(GetAllSongsRef ref) async {
  final token =
      ref.watch(currentUserNotifierProvider.select((user) => user!.token));
  final res = await ref.watch(homeRepositoryProvider).getAllSongs(
        token: token,
      );

  return switch (res) {
    Left(value: final l) => throw l.message,
    Right(value: final r) => r,
  };
}

@riverpod
class HomeViewModel extends _$HomeViewModel {
  late HomeRepository _homeRepository;
  late HomeLocalRepository _homeLocalRepository;
  @override
  AsyncValue? build() {
    _homeRepository = ref.watch(homeRepositoryProvider);
    _homeLocalRepository = ref.watch(homeLocalRepositoryProvider);
    return null;
  }

  Future<void> uploadSong({
    required File song,
    required File thumbnail,
    required String artist,
    required String songName,
    required Color color,
  }) async {
    state = const AsyncValue.loading();
    final res = await _homeRepository.uploadSong(
      song: song,
      thumbnail: thumbnail,
      artist: artist,
      songName: songName,
      hexCode: rgbToHex(color),
      token: ref.read(currentUserNotifierProvider)!.token,
    );

    final val = switch (res) {
      Left(value: final l) => state =
          AsyncValue.error(l.message.toString(), StackTrace.current),
      Right(value: final r) => state = AsyncValue.data(r),
    };

    print(val);
  }

  List<SongModel> getRecentlyPlayedSongs() {
    return _homeLocalRepository.loadSongs();
  }

  Future<void> favSong({required String songId}) async {
    state = const AsyncValue.loading();
    final res = await _homeRepository.favSong(
      songId: songId,
      token: ref.read(currentUserNotifierProvider)!.token,
    );

    final val = switch (res) {
      Left(value: final l) => state =
          AsyncValue.error(l.message, StackTrace.current),
      Right(value: final r) => _favSongSuccess(r, songId),
    };
    print(val);
  }

  AsyncValue _favSongSuccess(bool isFavorited, String songId) {
    final userNotifier = ref.read(currentUserNotifierProvider.notifier);
    if (isFavorited) {
      userNotifier.addUser(
        ref.read(currentUserNotifierProvider)!.copyWith(
          favorites: [
            ...ref.read(currentUserNotifierProvider)!.favorites,
            FavSongModel(
              id: '',
              song_id: songId,
              user_id: '',
            ),
          ],
        ),
      );
    } else {
      userNotifier.addUser(
        ref.read(currentUserNotifierProvider)!.copyWith(
              favorites: ref
                  .read(currentUserNotifierProvider)!
                  .favorites
                  .where(
                    (fav) => fav.song_id != songId,
                  )
                  .toList(),
            ),
      );
    }
    ref.invalidate(getFavSongsProvider);
    return state = AsyncValue.data(isFavorited);
  }
}
