/* ------------------------------------------------------------
name: "highgain_guitar"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn HighgainGuitar -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __HighgainGuitar_H__
#define  __HighgainGuitar_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS HighgainGuitar
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float HighgainGuitar_faustpower2_f(float value) {
	return value * value;
}

class HighgainGuitar : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst0;
	float fConst3;
	float fConst5;
	float fConst7;
	float fConst9;
	float fConst11;
	float fConst13;
	FAUSTFLOAT fHslider0;
	float fConst14;
	float fConst16;
	float fConst18;
	float fConst20;
	FAUSTFLOAT fHslider1;
	float fConst21;
	float fConst23;
	float fConst24;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec10[2];
	float fConst25;
	float fConst26;
	float fConst27;
	float fConst30;
	float fConst32;
	float fConst34;
	int iRec12[2];
	float fRec11[3];
	float fConst35;
	float fConst36;
	float fConst37;
	float fConst38;
	float fRec14[2];
	FAUSTFLOAT fHslider2;
	int IOTA0;
	float fVec1[8192];
	FAUSTFLOAT fHslider3;
	float fRec13[3];
	FAUSTFLOAT fHslider4;
	float fVec2[2];
	float fConst39;
	float fConst40;
	float fConst41;
	float fRec9[2];
	float fVec3[2];
	float fRec8[2];
	float fVec4[2];
	float fRec7[2];
	float fRec6[3];
	float fRec5[3];
	float fConst42;
	float fRec4[3];
	float fVec5[2];
	float fConst43;
	float fConst44;
	float fRec3[2];
	float fRec2[3];
	float fVec6[2];
	float fConst45;
	float fConst46;
	float fConst47;
	float fRec1[2];
	float fRec0[3];
	FAUSTFLOAT fHslider5;
	float fConst48;
	
 public:
	HighgainGuitar() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn HighgainGuitar -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "highgain_guitar.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/peak_eq:author", "Julius O. Smith III");
		m->declare("filters.lib/peak_eq:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/peak_eq:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "highgain_guitar");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(376.99112f / fConst0);
		float fConst2 = HighgainGuitar_faustpower2_f(fConst1);
		fConst3 = 2.0f * (1.0f - 1.0f / fConst2);
		float fConst4 = 1.0f / fConst1;
		fConst5 = (fConst4 + -1.0f) / fConst1 + 1.0f;
		float fConst6 = (fConst4 + 1.0f) / fConst1 + 1.0f;
		fConst7 = 1.0f / fConst6;
		float fConst8 = std::tan(20734.512f / fConst0);
		fConst9 = 2.0f * (1.0f - 1.0f / HighgainGuitar_faustpower2_f(fConst8));
		float fConst10 = 1.0f / fConst8;
		fConst11 = (fConst10 + -1.0f) / fConst8 + 1.0f;
		float fConst12 = (fConst10 + 1.0f) / fConst8 + 1.0f;
		fConst13 = 1.0f / fConst12;
		fConst14 = 3.1415927f / fConst0;
		float fConst15 = std::tan(9424.778f / fConst0);
		fConst16 = 2.0f * (1.0f - 1.0f / HighgainGuitar_faustpower2_f(fConst15));
		float fConst17 = 1.0f / fConst15;
		fConst18 = (fConst17 + -0.7692308f) / fConst15 + 1.0f;
		float fConst19 = (fConst17 + 0.7692308f) / fConst15 + 1.0f;
		fConst20 = 1.0f / fConst19;
		fConst21 = 2513.2742f / (fConst0 * std::sin(6283.1855f / fConst0));
		float fConst22 = std::tan(3141.5928f / fConst0);
		fConst23 = 1.0f / fConst22;
		fConst24 = 2.0f * (1.0f - 1.0f / HighgainGuitar_faustpower2_f(fConst22));
		fConst25 = std::max<float>(1.0f, 0.0004f * fConst0);
		fConst26 = 1.0f / fConst25;
		fConst27 = 1.0f / std::max<float>(1.0f, 0.005f * fConst0);
		float fConst28 = std::tan(8168.141f / fConst0);
		float fConst29 = HighgainGuitar_faustpower2_f(fConst28);
		fConst30 = 2.0f * (1.0f - 1.0f / fConst29);
		float fConst31 = 1.0f / fConst28;
		fConst32 = (fConst31 + -1.4142135f) / fConst28 + 1.0f;
		float fConst33 = (fConst31 + 1.4142135f) / fConst28 + 1.0f;
		fConst34 = 1.0f / fConst33;
		fConst35 = 0.6f / (fConst29 * fConst33);
		fConst36 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst37 = 1.0f / fConst36;
		fConst38 = 1.0f / std::max<float>(1.0f, 0.008f * fConst0);
		fConst39 = 1.0f / std::tan(219.91148f / fConst0);
		fConst40 = 1.0f - fConst39;
		fConst41 = 1.0f / (fConst39 + 1.0f);
		fConst42 = 2.0f / (fConst15 * fConst19);
		fConst43 = 1.0f - fConst10;
		fConst44 = 1.0f / (fConst10 + 1.0f);
		fConst45 = 1.0f / (fConst1 * fConst12);
		fConst46 = 1.0f - fConst4;
		fConst47 = 1.0f / (fConst4 + 1.0f);
		fConst48 = 0.12f / (fConst2 * fConst6);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.0f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider2 = FAUSTFLOAT(0.995f);
		fHslider3 = FAUSTFLOAT(82.0f);
		fHslider4 = FAUSTFLOAT(0.85f);
		fHslider5 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec10[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec12[l2] = 0;
		}
		for (int l3 = 0; l3 < 3; l3 = l3 + 1) {
			fRec11[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec14[l4] = 0.0f;
		}
		IOTA0 = 0;
		for (int l5 = 0; l5 < 8192; l5 = l5 + 1) {
			fVec1[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec13[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fVec2[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec9[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fVec3[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec8[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fVec4[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec7[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec6[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 3; l14 = l14 + 1) {
			fRec5[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 3; l15 = l15 + 1) {
			fRec4[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fVec5[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 2; l17 = l17 + 1) {
			fRec3[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 3; l18 = l18 + 1) {
			fRec2[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 2; l19 = l19 + 1) {
			fVec6[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 2; l20 = l20 + 1) {
			fRec1[l20] = 0.0f;
		}
		for (int l21 = 0; l21 < 3; l21 = l21 + 1) {
			fRec0[l21] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual HighgainGuitar* clone() {
		return new HighgainGuitar();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("highgain_guitar");
		ui_interface->addHorizontalSlider("drive", &fHslider4, FAUSTFLOAT(0.85f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider3, FAUSTFLOAT(82.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("mids", &fHslider1, FAUSTFLOAT(0.0f), FAUSTFLOAT(-1.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("mute", &fHslider0, FAUSTFLOAT(0.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("sustain", &fHslider2, FAUSTFLOAT(0.995f), FAUSTFLOAT(0.98f), FAUSTFLOAT(0.9985f), FAUSTFLOAT(0.0001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = std::tan(fConst14 * (6.9e+03f - 3.6e+03f * fSlow0));
		float fSlow2 = 2.0f * (1.0f - 1.0f / HighgainGuitar_faustpower2_f(fSlow1));
		float fSlow3 = 1.0f / fSlow1;
		float fSlow4 = (fSlow3 + -1.4142135f) / fSlow1 + 1.0f;
		float fSlow5 = 1.0f / ((fSlow3 + 1.4142135f) / fSlow1 + 1.0f);
		float fSlow6 = 1e+01f * float(fHslider1);
		int iSlow7 = fSlow6 > 0.0f;
		float fSlow8 = fConst21 * std::pow(1e+01f, 0.05f * std::fabs(fSlow6));
		float fSlow9 = ((iSlow7) ? fConst21 : fSlow8);
		float fSlow10 = fConst23 * (fConst23 + fSlow9) + 1.0f;
		float fSlow11 = ((iSlow7) ? fSlow8 : fConst21);
		float fSlow12 = fConst23 * (fConst23 - fSlow11) + 1.0f;
		float fSlow13 = fConst23 * (fConst23 - fSlow9) + 1.0f;
		float fSlow14 = float(fButton0);
		float fSlow15 = 1.0f / std::tan(fConst14 * std::max<float>(0.12f, fSlow14) * (3e+03f * (1.0f - fSlow0) + 3.2e+03f));
		float fSlow16 = 1.0f - fSlow15;
		float fSlow17 = 1.0f / (fSlow15 + 1.0f);
		float fSlow18 = float(fHslider2) - 0.06f * fSlow0;
		float fSlow19 = fConst0 / float(fHslider3);
		float fSlow20 = fSlow19 + -2.0f;
		int iSlow21 = int(fSlow20);
		int iSlow22 = std::min<int>(4097, std::max<int>(0, iSlow21 + 1));
		float fSlow23 = std::floor(fSlow20);
		float fSlow24 = fSlow19 + (-2.0f - fSlow23);
		int iSlow25 = std::min<int>(4097, std::max<int>(0, iSlow21));
		float fSlow26 = fSlow23 + (3.0f - fSlow19);
		float fSlow27 = 21.0f * float(fHslider4) + 3.0f;
		float fSlow28 = fConst23 * (fConst23 + fSlow11) + 1.0f;
		float fSlow29 = fConst48 * float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = fConst24 * fRec6[1];
			fVec0[0] = fSlow14;
			iRec10[0] = (iRec10[1] + (iRec10[1] > 0)) * (fSlow14 <= fVec0[1]) + (fSlow14 > fVec0[1]);
			float fTemp1 = float(iRec10[0]);
			iRec12[0] = 1103515245 * iRec12[1] + 12345;
			float fTemp2 = float(iRec12[0]);
			fRec11[0] = 4.656613e-10f * fTemp2 - fConst34 * (fConst32 * fRec11[2] + fConst30 * fRec11[1]);
			fRec14[0] = -(fSlow17 * (fSlow16 * fRec14[1] - (fRec13[1] + fRec13[2])));
			float fTemp3 = fSlow18 * fRec14[0] + 4.656613e-10f * fTemp2 * std::max<float>(0.0f, std::min<float>(fConst37 * fTemp1, fConst38 * (fConst36 - fTemp1) + 1.0f));
			fVec1[IOTA0 & 8191] = fTemp3;
			fRec13[0] = fSlow26 * fVec1[(IOTA0 - iSlow25) & 8191] + fSlow24 * fVec1[(IOTA0 - iSlow22) & 8191];
			float fTemp4 = tanhf(fSlow27 * (fRec13[0] + fConst35 * (fRec11[2] + (fRec11[0] - 2.0f * fRec11[1])) * std::max<float>(0.0f, std::min<float>(fConst26 * fTemp1, fConst27 * (fConst25 - fTemp1) + 1.0f))) + 0.12f);
			fVec2[0] = fTemp4;
			fRec9[0] = -(fConst41 * (fConst40 * fRec9[1] - fConst39 * (fTemp4 - fVec2[1])));
			float fTemp5 = tanhf(fSlow27 * fRec9[0] + 0.12f);
			fVec3[0] = fTemp5;
			fRec8[0] = -(fConst41 * (fConst40 * fRec8[1] - fConst39 * (fTemp5 - fVec3[1])));
			float fTemp6 = tanhf(fSlow27 * fRec8[0] + 0.12f);
			fVec4[0] = fTemp6;
			fRec7[0] = -(fConst41 * (fConst40 * fRec7[1] - fConst39 * (fTemp6 - fVec4[1])));
			fRec6[0] = fRec7[0] - (fRec6[2] * fSlow13 + fTemp0) / fSlow10;
			float fTemp7 = (fTemp0 + fRec6[0] * fSlow28 + fRec6[2] * fSlow12) / fSlow10;
			fRec5[0] = fTemp7 - fConst20 * (fConst18 * fRec5[2] + fConst16 * fRec5[1]);
			fRec4[0] = fTemp7 + fConst42 * (fRec5[0] - fRec5[2]) - fSlow5 * (fSlow4 * fRec4[2] + fSlow2 * fRec4[1]);
			float fTemp8 = fSlow5 * (fRec4[2] + fRec4[0] + 2.0f * fRec4[1]);
			fVec5[0] = fTemp8;
			fRec3[0] = -(fConst44 * (fConst43 * fRec3[1] - (fTemp8 + fVec5[1])));
			fRec2[0] = fRec3[0] - fConst13 * (fConst11 * fRec2[2] + fConst9 * fRec2[1]);
			float fTemp9 = fRec2[2] + fRec2[0] + 2.0f * fRec2[1];
			fVec6[0] = fTemp9;
			fRec1[0] = -(fConst47 * (fConst46 * fRec1[1] - fConst45 * (fTemp9 - fVec6[1])));
			fRec0[0] = fRec1[0] - fConst7 * (fConst5 * fRec0[2] + fConst3 * fRec0[1]);
			float fTemp10 = fSlow29 * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp10);
			output1[i0] = FAUSTFLOAT(fTemp10);
			fVec0[1] = fVec0[0];
			iRec10[1] = iRec10[0];
			iRec12[1] = iRec12[0];
			fRec11[2] = fRec11[1];
			fRec11[1] = fRec11[0];
			fRec14[1] = fRec14[0];
			IOTA0 = IOTA0 + 1;
			fRec13[2] = fRec13[1];
			fRec13[1] = fRec13[0];
			fVec2[1] = fVec2[0];
			fRec9[1] = fRec9[0];
			fVec3[1] = fVec3[0];
			fRec8[1] = fRec8[0];
			fVec4[1] = fVec4[0];
			fRec7[1] = fRec7[0];
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fVec5[1] = fVec5[0];
			fRec3[1] = fRec3[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fVec6[1] = fVec6[0];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
