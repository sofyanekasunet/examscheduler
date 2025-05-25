"""Streamlit UI u2013 updated for new template & improved visualisation."""
from __future__ import annotations

import io
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from excel_io import read_input_workbook, write_schedule
from i18n import _
from logging_utils import get_log_buffer, reset_log_buffer, log
from scheduler import build_schedule

st.set_page_config(page_title="Exam Scheduler", layout="wide")

# -----------------------------------------------------------------------------
# Sidebar controls
# -----------------------------------------------------------------------------
lang = st.sidebar.selectbox("U0001F310 Language / اللغة", ["FR", "AR"])
uploaded = st.sidebar.file_uploader(_("upload", lang), type=["xlsx"])
time_limit = st.sidebar.slider(_("time_limit", lang), 1, 30, 10)

def show_df(df: pd.DataFrame):
    st.dataframe(df.style.set_properties(**{"text-align": "center"}), use_container_width=True)

# -----------------------------------------------------------------------------
# Main flow
# -----------------------------------------------------------------------------
if uploaded:
    # Save to temp path using tempfile module for cross-platform compatibility
    temp_dir = tempfile.gettempdir()
    source = Path(temp_dir) / uploaded.name
    with open(source, "wb") as f:
        f.write(uploaded.getbuffer())

    input_data = read_input_workbook(source)
    st.success(_("file_loaded", lang) + f" u2013 {len(input_data.teachers)} {_("teachers", lang)}, {len(input_data.rooms)} {_("rooms", lang)}, {len(input_data.sessions)} {_("sessions", lang)}")

    if st.sidebar.button(_("generate", lang)):
        reset_log_buffer()
        try:
            # Pass attributes from input_data directly
            schedule = build_schedule(
                input_data.teachers,
                input_data.sessions,
                input_data.rooms,
                input_data.active_pairs,
                time_limit=time_limit # Assuming time_limit is still a separate param for build_schedule
            )
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            out_path = Path(temp_dir) / f"scheduled_{ts}.xlsx"
            write_schedule(source, input_data, schedule, out_path)

            # Visual u2013 Distribution grid as DataFrame
            grid = {}
            for room in input_data.rooms:
                grid[room] = [" / ".join(schedule.supervisors.get((room, s), [])) for s in input_data.sessions]
            df_grid = pd.DataFrame(grid, index=input_data.sessions).T  # rooms as rows
            st.subheader("U0001F5FA️ Distribution grid")
            show_df(df_grid)

            # Visual u2013 workload bar chart
            st.subheader("U0001F4CA Teacher workload")
            # Assuming schedule object has 'load' attribute as a dict
            df_load = pd.DataFrame(list(schedule.load.items()), columns=["Teacher", "Load"])
            df_load_sorted = df_load.sort_values("Load", ascending=False)
            st.bar_chart(df_load_sorted, x="Teacher", y="Load")

            # Download button
            with open(out_path, "rb") as f:
                st.download_button(_("download", lang), data=f, file_name=out_path.name)

        except ValueError as err:
            st.error(str(err))
            log(str(err))

    st.expander(_("log", lang)).write(get_log_buffer().getvalue())
else:
    st.info(_("upload_prompt", lang))