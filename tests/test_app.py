import pytest
import pygame

from app import CollingwoodFractalApp
from config import DEFAULT_CENTER, DEFAULT_SCALE
from fractal import screen_to_complex


def test_palette_selection_updates_both_palettes():
    app = CollingwoodFractalApp(width=1200, height=900, max_iter=220)

    app.set_palette("Sunset", "fractal")
    app.set_palette("Ice", "background")

    assert app.fractal_palette.name == "Sunset"
    assert app.background_palette.name == "Ice"


def test_iteration_change_for_unicode_keys():
    app = CollingwoodFractalApp(width=1200, height=900, max_iter=220)

    app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_0, unicode="+"))
    assert app.max_iter == 270

    app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_0, unicode="-"))
    assert app.max_iter == 220


def test_quick_iteration_presets():
    app = CollingwoodFractalApp(width=1200, height=900, max_iter=220)

    app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1, unicode="1"))
    assert app.max_iter == 20

    app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2, unicode="2"))
    assert app.max_iter == 220


def test_russian_layout_keys_do_not_close_app():
    app = CollingwoodFractalApp(width=1200, height=900, max_iter=220)

    app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, unicode="й"))
    assert app.running is True

    app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, unicode="у"))
    assert app.running is True


def test_zoom_keeps_cursor_target():
    app = CollingwoodFractalApp(width=1200, height=900, max_iter=220)

    px = 320
    py = 200
    old_scale = app.scale
    old_center_x, old_center_y = app.center_x, app.center_y

    render_x = px * (app.render_width / (app.width - app.menu_width))
    render_y = (py - app.hud_height) * (app.render_height / (app.height - app.hud_height))
    target_x, target_y = screen_to_complex(
        render_x,
        render_y,
        app.render_width,
        app.render_height,
        old_center_x,
        old_center_y,
        old_scale,
    )

    u = render_x / app.render_width - 0.5
    v = render_y / app.render_height - 0.5
    expected_center_x = target_x - u * (old_scale / 2.0)
    expected_center_y = target_y - v * (old_scale * (app.render_height / app.render_width) / 2.0)

    app.zoom_at(px, py, 2.0)

    assert app.center_x == pytest.approx(expected_center_x)
    assert app.center_y == pytest.approx(expected_center_y)


def test_zoom_target_tracks_click_on_left_side():
    app = CollingwoodFractalApp(width=1200, height=900, max_iter=220)

    old_center_x, old_center_y, old_scale = app.center_x, app.center_y, app.scale
    px = 80
    py = 260

    render_x = (px / (app.width - app.menu_width)) * app.render_width
    render_y = ((py - app.hud_height) / (app.height - app.hud_height)) * app.render_height
    target_x, target_y = screen_to_complex(
        render_x,
        render_y,
        app.render_width,
        app.render_height,
        old_center_x,
        old_center_y,
        old_scale,
    )

    app.zoom_at(px, py, 2.0)

    assert app.center_x < old_center_x
    assert app.center_y < old_center_y
    assert app.scale == pytest.approx(old_scale / 2.0)

    after_target_x, after_target_y = screen_to_complex(
        render_x,
        render_y,
        app.render_width,
        app.render_height,
        app.center_x,
        app.center_y,
        app.scale,
    )
    assert after_target_x == pytest.approx(target_x)
    assert after_target_y == pytest.approx(target_y)


def test_move_center_by_arrow_navigation():
    app = CollingwoodFractalApp(width=1200, height=900, max_iter=220)

    before_x, before_y = app.center_x, app.center_y
    app.move_center("right")

    assert app.center_x < before_x
    assert app.center_y == before_y

    before_x, before_y = app.center_x, app.center_y
    app.move_center("up")

    assert app.center_x == before_x
    assert app.center_y > before_y


def test_center_resets_zoom_and_center():
    app = CollingwoodFractalApp(width=1200, height=900, max_iter=220)
    app.zoom_at(300, 250, 2.0)
    app.move_center("center")

    assert app.center_x == pytest.approx(DEFAULT_CENTER[0])
    assert app.center_y == pytest.approx(DEFAULT_CENTER[1])
    assert app.scale == pytest.approx(DEFAULT_SCALE)


def test_click_only_selects_point_without_direct_zoom():
    app = CollingwoodFractalApp(width=1200, height=900, max_iter=220)

    before_scale = app.scale
    before_center = app.center_x, app.center_y

    app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(200, 220), button=1))

    assert app.selected_point == (200, 220)
    assert app.scale == before_scale
    assert app.center_x == before_center[0]
    assert app.center_y == before_center[1]


def test_auto_zoom_uses_selected_point():
    app = CollingwoodFractalApp(width=1200, height=900, max_iter=220)

    before_scale = app.scale
    before_center_x, before_center_y = app.center_x, app.center_y
    app.set_selected_point(320, 220)

    app.auto_zoom_selected(2.0)

    assert app.scale == pytest.approx(before_scale / 2.0)
    assert app.center_x != before_center_x or app.center_y != before_center_y


def test_menu_action_dispatch_uses_button_name():
    app = CollingwoodFractalApp(width=1200, height=900, max_iter=220)
    app.set_selected_point(320, 220)

    before_scale = app.scale
    before_center = app.center_x, app.center_y
    app.trigger_menu_action("auto_zoom")

    assert app.scale < before_scale
    assert app.center_x != before_center[0] or app.center_y != before_center[1]
