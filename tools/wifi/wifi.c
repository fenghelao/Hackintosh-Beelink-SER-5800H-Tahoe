#include <stdio.h>
#include <string.h>
#include "Api.h"
int main(int argc, char **argv) {
    if (argc >= 4 && !strcmp(argv[1], "assoc")) { printf("associate_ssid -> %#x\n", associate_ssid(argv[2], argv[3])); return 0; }
    if (argc >= 3 && !strcmp(argv[1], "disassoc")) { printf("dis_associate -> %#x\n", dis_associate_ssid(argv[2])); return 0; }
    uint32_t st = 0; get_80211_state(&st); char ssid[64] = {0}; get_network_ssid(ssid);
    station_info_t sta; memset(&sta, 0, sizeof(sta)); get_station_info(&sta);
    printf("state=%u (4=RUN) ssid=%s chan=%u bw=%u rssi=%d rate=%u mode=%d\n", st, ssid, sta.channel, sta.band_width, sta.rssi, sta.rate, sta.op_mode);
    static network_info_list_t list; memset(&list, 0, sizeof(list)); get_network_list(&list);
    printf("%d networks\n%-28s ch  rssi protos akms supp_akms ciphers group mgmt caps\n", list.count, "ssid");
    for (int i = 0; i < list.count; i++) { struct ioctl_network_info *n = &list.networks[i];
        if (argc >= 2 && !strstr((char*)n->ssid, argv[1])) continue;
        printf("%-28.32s %3u %4d %#6x %#4x %#9x %#7x %#5x %#4x %#06x  bssid %02x:%02x:%02x:%02x:%02x:%02x\n", n->ssid, n->channel, n->rssi, n->rsn_protos, n->rsn_akms, n->supported_rsnakms,
               n->rsn_ciphers, n->rsn_groupcipher, n->rsn_groupmgmtcipher, n->ni_rsncaps, n->bssid[0],n->bssid[1],n->bssid[2],n->bssid[3],n->bssid[4],n->bssid[5]); }
    return 0;
}
