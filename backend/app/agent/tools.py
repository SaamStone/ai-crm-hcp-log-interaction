"""
The five LangGraph tools that drive the Log HCP Interaction screen.

Every tool operates on a single shared `form` dict (a mirror of the React/Redux
form state for the current request) and appends the names of any fields it
touches to `changed` so the API layer can tell the frontend exactly which
inputs to highlight/update. Tools never talk to the user directly - their
return value is a short natural-language summary that the LLM reads and turns
into its own reply.
"""

from difflib import SequenceMatcher
from typing import Optional

from langchain_core.tools import tool

SENTIMENT_VALUES = {"positive", "neutral", "negative"}
FIELD_LABELS = {
    "hcp_name": "HCP Name",
    "interaction_type": "Interaction Type",
    "date": "Date",
    "time": "Time",
    "attendees": "Attendees",
    "topics_discussed": "Topics Discussed",
    "sentiment": "Sentiment",
    "outcomes": "Outcomes",
    "follow_up_actions": "Follow-up Actions",
}


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def build_tools(form: dict, changed: list[str], hcp_directory: list[dict]):
    """Factory that returns the 5 tool objects bound to this request's mutable
    form/changed-fields state (kept isolated per-request rather than global)."""

    # ---------------------------------------------------------------- Tool 1
    @tool
    def log_interaction(
        hcp_name: Optional[str] = None,
        interaction_type: Optional[str] = None,
        date: Optional[str] = None,
        time: Optional[str] = None,
        attendees: Optional[str] = None,
        topics_discussed: Optional[str] = None,
        materials_shared: Optional[list[str]] = None,
        samples_distributed: Optional[list[str]] = None,
        sentiment: Optional[str] = None,
        outcomes: Optional[str] = None,
        follow_up_actions: Optional[str] = None,
    ) -> str:
        """Log a brand-new HCP interaction from the rep's free-text description.

        Call this the FIRST time the user describes a visit/call/meeting in a
        sentence or two. Extract every field you can genuinely infer from their
        message - HCP name, interaction_type (Meeting/Call/Email/Conference),
        date, time, attendees, topics_discussed, materials_shared,
        samples_distributed, sentiment (Positive/Neutral/Negative, inferred from
        tone), outcomes, follow_up_actions. Leave a parameter unset if the user
        did not mention it - never invent data.
        """
        provided = {
            "hcp_name": hcp_name,
            "interaction_type": interaction_type,
            "date": date,
            "time": time,
            "attendees": attendees,
            "topics_discussed": topics_discussed,
            "sentiment": sentiment.capitalize() if sentiment else None,
            "outcomes": outcomes,
            "follow_up_actions": follow_up_actions,
        }
        touched = []
        for key, value in provided.items():
            if value is not None and str(value).strip() != "":
                form[key] = value
                touched.append(key)

        if materials_shared:
            form["materials_shared"] = list(dict.fromkeys(form.get("materials_shared", []) + materials_shared))
            touched.append("materials_shared")
        if samples_distributed:
            form["samples_distributed"] = list(dict.fromkeys(form.get("samples_distributed", []) + samples_distributed))
            touched.append("samples_distributed")

        changed.extend(touched)
        if not touched:
            return "No usable interaction details were found in that message - ask the user for at least an HCP name and what was discussed."

        labels = ", ".join(FIELD_LABELS.get(f, f) for f in touched if f in FIELD_LABELS or f in ("materials_shared", "samples_distributed"))
        return f"Interaction logged. Fields populated: {labels}."

    # ---------------------------------------------------------------- Tool 2
    @tool
    def edit_interaction(
        hcp_name: Optional[str] = None,
        interaction_type: Optional[str] = None,
        date: Optional[str] = None,
        time: Optional[str] = None,
        attendees: Optional[str] = None,
        topics_discussed: Optional[str] = None,
        sentiment: Optional[str] = None,
        outcomes: Optional[str] = None,
        follow_up_actions: Optional[str] = None,
    ) -> str:
        """Correct or update fields on an interaction that is already partially
        or fully logged on the form.

        Call this when the user is fixing/changing something they (or the AI)
        said earlier - e.g. "sorry the name was actually John" or "change the
        sentiment to negative". ONLY pass the parameters that should change;
        every field you leave unset stays exactly as it is on the form. Do not
        re-send fields that aren't being corrected.
        """
        provided = {
            "hcp_name": hcp_name,
            "interaction_type": interaction_type,
            "date": date,
            "time": time,
            "attendees": attendees,
            "topics_discussed": topics_discussed,
            "sentiment": sentiment.capitalize() if sentiment else None,
            "outcomes": outcomes,
            "follow_up_actions": follow_up_actions,
        }
        diffs = []
        for key, value in provided.items():
            if value is not None and str(value).strip() != "":
                old = form.get(key)
                form[key] = value
                changed.append(key)
                label = FIELD_LABELS.get(key, key)
                diffs.append(f"{label}: '{old or 'empty'}' -> '{value}'")

        if not diffs:
            return "No fields were changed - I couldn't tell which field the correction applied to, ask the user to clarify."
        return "Updated the following field(s): " + "; ".join(diffs)

    # ---------------------------------------------------------------- Tool 3
    @tool
    def lookup_hcp(name_query: str) -> str:
        """Search the HCP master directory by (partial/misspelled) name.

        Use this to validate the spelling of an HCP's name, find their
        specialty/hospital, or resolve ambiguity before/after logging. If
        exactly one high-confidence match is found, this automatically sets
        the HCP Name field to the canonical, correctly-spelled name.
        """
        scored = sorted(
            ({**h, "score": _similar(name_query, h["name"])} for h in hcp_directory),
            key=lambda h: h["score"],
            reverse=True,
        )
        top = [h for h in scored if h["score"] > 0.45][:3]
        if not top:
            return f"No HCP matching '{name_query}' was found in the directory. Ask the user to confirm the spelling, or proceed treating it as a new HCP."

        if len(top) == 1 or top[0]["score"] - (top[1]["score"] if len(top) > 1 else 0) > 0.2:
            best = top[0]
            form["hcp_name"] = best["name"]
            changed.append("hcp_name")
            return f"Matched to {best['name']} ({best['specialty']}, {best['hospital']}). HCP Name field set to this canonical name."

        options = "; ".join(f"{h['name']} ({h['specialty']})" for h in top)
        return f"Multiple possible matches found: {options}. Ask the user which one they mean."

    # ---------------------------------------------------------------- Tool 4
    @tool
    def manage_materials_samples(
        materials_to_add: Optional[list[str]] = None,
        samples_to_add: Optional[list[str]] = None,
    ) -> str:
        """Add materials (brochures, leave-behinds, literature) and/or samples
        distributed to the interaction record.

        Use this whenever the user mentions handing over/sharing/leaving
        something with the HCP, even in passing. Items are appended to
        whatever is already listed - nothing is overwritten or removed.
        """
        added = []
        if materials_to_add:
            new = [m for m in materials_to_add if m not in form.get("materials_shared", [])]
            form["materials_shared"] = form.get("materials_shared", []) + new
            if new:
                changed.append("materials_shared")
                added.append(f"materials: {', '.join(new)}")
        if samples_to_add:
            new = [s for s in samples_to_add if s not in form.get("samples_distributed", [])]
            form["samples_distributed"] = form.get("samples_distributed", []) + new
            if new:
                changed.append("samples_distributed")
                added.append(f"samples: {', '.join(new)}")

        if not added:
            return "Nothing new to add - no material or sample names were provided."
        return "Added " + " and ".join(added) + "."

    # ---------------------------------------------------------------- Tool 5
    @tool
    def suggest_follow_up(reasoning: Optional[str] = None) -> str:
        """Propose the next-best-action follow-up for this HCP and write it
        into the Follow-up Actions field.

        Call this when the user asks for a suggestion, or says yes/agrees after
        you've offered to suggest a follow-up. Base the suggestion on the
        sentiment and topics_discussed already captured on the form. Pass a
        short `reasoning` describing why (e.g. "positive sentiment on Product X
        efficacy warrants a closer follow-up").
        """
        sentiment = (form.get("sentiment") or "Neutral").lower()
        topic = form.get("topics_discussed") or "the topics discussed"

        if sentiment == "positive":
            suggestion = f"Schedule a follow-up meeting within 2 weeks to provide deeper clinical data on {topic}."
        elif sentiment == "negative":
            suggestion = f"Escalate to Medical Affairs for a detailed follow-up addressing concerns about {topic} before re-engaging."
        else:
            suggestion = f"Send a follow-up email with supporting literature on {topic} and check back in 3-4 weeks."

        form["follow_up_actions"] = suggestion
        changed.append("follow_up_actions")
        note = f" ({reasoning})" if reasoning else ""
        return f"Follow-up Actions field set to: '{suggestion}'{note}"

    return [log_interaction, edit_interaction, lookup_hcp, manage_materials_samples, suggest_follow_up]
