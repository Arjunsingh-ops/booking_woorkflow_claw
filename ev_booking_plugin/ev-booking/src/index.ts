import { Type } from "typebox";
import { defineToolPlugin } from "openclaw/plugin-sdk/tool-plugin";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export default defineToolPlugin({
  id: "ev-booking",
  name: "EV Booking",
  description: "Execute the EV Booking workflow.",

  tools: (tool) => [
    tool({
      name: "book_ev_slot",

      description:
        "Books an EV charging slot using the existing BookingAgent workflow.",

      parameters: Type.Object({
        request: Type.String({
          description: "Natural language booking request.",
        }),
      }),

      execute: async ({ request }) => {
        const { stdout } = await execFileAsync(
          "/mnt/d/booking-workflow-claw/.venv/bin/python",
          [
            "/mnt/d/booking-workflow-claw/app_openclaw.py",
            request,
          ]
        );

        return JSON.parse(stdout);
      },
    }),
  ],
});
